import stripe
import datetime
import logging
from django.conf import settings
from django.utils.timezone import make_aware
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions

from .models import *
from .serializers import *
import os
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

load_dotenv()

stripe.api_key = os.getenv("STRIPE_API_KEY")



class PlanListCreateView(generics.ListCreateAPIView):
    queryset = Plan.objects.filter(active=True)
    serializer_class = PlanSerializer

    def create(self, request, *args, **kwargs):
        """
        Create Stripe Product + Price, then save in Plan model.
        """
        name = request.data.get("name")
        interval = request.data.get("interval")  # "month" or "year"
        amount_usd = request.data.get("amount")  # in USD
        if amount_usd is not None:
          try:
            amount = int(float(amount_usd) * 100)  # convert USD to cents
          except ValueError:
            return Response({"error": "Invalid amount format"}, status=400)
        else:
          amount = None
        trial_days = request.data.get("trial_days", 0)

        if not all([name, interval, amount]):
            return Response({"error": "name, interval, amount required"}, status=400)

        try:
            product = stripe.Product.create(name=name)

            price = stripe.Price.create(
                product=product.id,
                unit_amount=int(amount),
                currency="usd",
                recurring={"interval": interval},
            )

            plan = Plan.objects.create(
                  name=name,
                  stripe_product_id=product.id,
                  stripe_price_id=price.id,
                  amount=int(amount),
                  interval=interval,
                  trial_days=trial_days,
                  active=True
                  )


            serializer = self.get_serializer(plan)
            return Response(serializer.data, status=201)

        except Exception as e:
            return Response({"error": str(e)}, status=400)


class PlanUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanUpdateSerializer
    lookup_field = "id"

    def perform_update(self, serializer):
        plan = self.get_object()
        old_amount = getattr(plan, "amount", None)

        updated_plan = serializer.save()

        try:
            # Update Stripe Product name
            stripe.Product.modify(
                plan.stripe_product_id,
                name=updated_plan.name
            )

            # If amount changed, create a new Stripe Price
            if "amount" in self.request.data and int(self.request.data["amount"]) != old_amount:
                new_price = stripe.Price.create(
                    product=plan.stripe_product_id,
                    unit_amount=int(self.request.data["amount"]),
                    currency="usd",
                    recurring={"interval": updated_plan.interval}
                )
                updated_plan.stripe_price_id = new_price.id
                updated_plan.save()

        except Exception as e:
            # Log error but don't block update
            print("Stripe update error:", e)



class CreateSubscriptionView(APIView):
    def post(self, request):
        plan_id = request.data.get("plan_id")  # Pass Plan PK from frontend
        success_url = request.data.get("success_url", f"{request.build_absolute_uri('/api/payment/payment-success/')}")
        cancel_url = request.data.get("cancel_url", f"{request.build_absolute_uri('/api/payment/payment-cancel/')}")
        
        try:
            plan = Plan.objects.get(pk=plan_id, active=True)
        except Plan.DoesNotExist:
            return Response({"error": "Plan not found"}, status=404)

        # Check if user already has an active subscription or trial
        existing_subscription = Subscription.get_user_active_subscription(request.user)
        
        if existing_subscription:
            error_data = {
                "current_plan": existing_subscription.plan.name if existing_subscription.plan else "Unknown",
                "status": existing_subscription.status,
                "subscription_id": existing_subscription.id
            }
            
            if existing_subscription.is_trial():
                error_data.update({
                    "error": "You already have an active trial period",
                    "message": "You cannot create a new subscription while your trial is active",
                    "trial_end": existing_subscription.trial_end
                })
            elif existing_subscription.is_paid_active():
                error_data.update({
                    "error": "You already have an active subscription",
                    "message": "You cannot create a new subscription while you have an active plan",
                    "current_period_end": existing_subscription.current_period_end
                })
            
            return Response(error_data, status=400)

        try:
            # ✅ Create or get Stripe customer
            customer = None
            existing_sub = Subscription.objects.filter(user=request.user).first()
            
            if existing_sub and existing_sub.stripe_customer_id:
                # Use existing customer
                customer_id = existing_sub.stripe_customer_id
                customer = stripe.Customer.retrieve(customer_id)
            else:
                # Create new customer
                customer = stripe.Customer.create(
                    email=request.user.email,
                    name=getattr(request.user, "full_name", None) or request.user.email,
                    metadata={
                        "user_id": request.user.id,
                        "plan_id": plan.id
                    }
                )

            # ✅ Create Stripe Checkout Session with trial period
            checkout_session = stripe.checkout.Session.create(
                customer=customer.id,
                payment_method_types=['card'],
                line_items=[{
                    'price': plan.stripe_price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=cancel_url,
                subscription_data={
                    'trial_period_days': plan.trial_days,
                    'metadata': {
                        'user_id': request.user.id,
                        'plan_id': plan.id,
                    }
                },
                metadata={
                    'user_id': request.user.id,
                    'plan_id': plan.id,
                },
                # Enable automatic tax calculation (optional)
                automatic_tax={'enabled': False},
                # Customer can update payment method
                allow_promotion_codes=True,
            )

            # ✅ Save pending subscription in DB (will be updated by webhook)
            subscription = Subscription.objects.create(
                user=request.user,
                plan=plan,
                stripe_customer_id=customer.id,
                stripe_subscription_id=None,  # Will be set by webhook
                status="pending",  # Will be updated to "trialing" by webhook
                trial_end=None,  # Will be set by webhook
                current_period_end=None,  # Will be set by webhook
            )

            return Response({
                "checkout_url": checkout_session.url,
                "checkout_session_id": checkout_session.id,
                "subscription_id": subscription.id,
                "plan": plan.name,
                "trial_days": plan.trial_days,
                "message": f"Redirecting to Stripe checkout with {plan.trial_days} days trial period"
            }, status=201)

        except stripe.error.StripeError as e:
            return Response({"error": f"Stripe error: {str(e)}"}, status=400)
        except KeyError as e:
            return Response({"error": f"Missing field: {str(e)}"}, status=400)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class CheckoutSessionStatusView(APIView):
    """Check the status of a Stripe checkout session"""
    def get(self, request):
        session_id = request.query_params.get('session_id')
        
        if not session_id:
            return Response({"error": "session_id is required"}, status=400)
        
        try:
            # Retrieve the checkout session from Stripe
            session = stripe.checkout.Session.retrieve(session_id)
            
            if session.payment_status == 'paid' and session.subscription:
                # Get the subscription from Stripe
                stripe_subscription = stripe.Subscription.retrieve(session.subscription)
                
                # Update our database subscription
                user_id = session.metadata.get('user_id')
                if user_id:
                    subscription = Subscription.objects.filter(
                        user_id=user_id,
                        status='pending'
                    ).first()
                    
                    if subscription:
                        subscription.stripe_subscription_id = stripe_subscription.id
                        subscription.status = stripe_subscription.status
                        subscription.trial_end = make_aware(
                            datetime.datetime.fromtimestamp(stripe_subscription.trial_end)
                        ) if stripe_subscription.trial_end else None
                        subscription.current_period_end = make_aware(
                            datetime.datetime.fromtimestamp(stripe_subscription.current_period_end)
                        ) if stripe_subscription.current_period_end else None
                        subscription.save()
                        
                        return Response({
                            "success": True,
                            "subscription": {
                                "id": subscription.id,
                                "status": subscription.status,
                                "trial_end": subscription.trial_end,
                                "current_period_end": subscription.current_period_end,
                                "plan_name": subscription.plan.name
                            }
                        }, status=200)
            
            return Response({
                "success": False,
                "payment_status": session.payment_status,
                "session_status": session.status
            }, status=200)
            
        except stripe.error.StripeError as e:
            return Response({"error": f"Stripe error: {str(e)}"}, status=400)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class UserSubscriptionStatusView(APIView):
    """Get current user's subscription status"""
    def get(self, request):
        try:
            active_subscription = Subscription.get_user_active_subscription(request.user)
            
            if not active_subscription:
                return Response({
                    "has_subscription": False,
                    "message": "No active subscription found"
                }, status=200)
            
            return Response({
                "has_subscription": True,
                "subscription": {
                    "id": active_subscription.id,
                    "plan_name": active_subscription.plan.name if active_subscription.plan else "Unknown",
                    "status": active_subscription.status,
                    "is_trial": active_subscription.is_trial(),
                    "is_paid_active": active_subscription.is_paid_active(),
                    "trial_end": active_subscription.trial_end,
                    "current_period_end": active_subscription.current_period_end,
                    "created_at": active_subscription.created_at
                }
            }, status=200)
            
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class PaymentSuccessView(APIView):
    permission_classes = [permissions.AllowAny]
    """Handle successful payment completion"""
    def get(self, request):
        return Response({"message": "Payment successful"}, status=200)


class PaymentCancelView(APIView):
      permission_classes = [permissions.AllowAny]
      """Handle cancelled payment"""
      def get(self, request):
            return Response({"message": "Payment cancel"}, status=200)


# ✅ Stripe Webhook
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    logger.info(f"Webhook received - Signature: {sig_header is not None}, Secret configured: {endpoint_secret is not None}")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        logger.info(f"Webhook event constructed successfully: {event.get('type', 'unknown')}")
    except ValueError as e:
        logger.error(f"Invalid payload: {str(e)}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {str(e)}")
        return HttpResponse(status=400)
    except Exception as e:
        logger.error(f"Webhook construction error: {str(e)}")
        return HttpResponse(status=400)

    try:
        # ✅ Save event in DB for debugging/logging
        WebhookEvent.objects.create(
            event_id=event["id"],
            type=event["type"],
            data=event["data"]["object"],
        )
        logger.info(f"Webhook event saved to database: {event['id']}")
    except Exception as e:
        logger.error(f"Failed to save webhook event: {str(e)}")
        # Don't return error here, continue processing

    obj = event["data"]["object"]
    event_type = event["type"]
    
    logger.info(f"Processing webhook event: {event_type}")

    try:
        # ✅ Handle checkout session completed
        if event_type == "checkout.session.completed":
            logger.info("Processing checkout.session.completed")
            
            # Get user from metadata
            metadata = obj.get("metadata", {})
            user_id = metadata.get("user_id")
            plan_id = metadata.get("plan_id")
            
            logger.info(f"Checkout metadata - user_id: {user_id}, plan_id: {plan_id}")
            
            if user_id and obj.get("subscription"):
                try:
                    # Retrieve the subscription from Stripe
                    stripe_subscription = stripe.Subscription.retrieve(obj["subscription"])
                    logger.info(f"Retrieved Stripe subscription: {stripe_subscription.id}")
                    
                    # Update the pending subscription in our database
                    subscription = Subscription.objects.filter(
                        user_id=user_id,
                        status="pending"
                    ).first()
                    
                    if subscription:
                        # Safely handle timestamps
                        trial_end = None
                        current_period_end = None
                        
                        if hasattr(stripe_subscription, 'trial_end') and stripe_subscription.trial_end:
                            trial_end = make_aware(
                                datetime.datetime.fromtimestamp(stripe_subscription.trial_end)
                            )
                        
                        if hasattr(stripe_subscription, 'current_period_end') and stripe_subscription.current_period_end:
                            current_period_end = make_aware(
                                datetime.datetime.fromtimestamp(stripe_subscription.current_period_end)
                            )
                        
                        subscription.stripe_subscription_id = stripe_subscription.id
                        subscription.status = stripe_subscription.status
                        subscription.trial_end = trial_end
                        subscription.current_period_end = current_period_end
                        subscription.save()
                        
                        logger.info(f"Updated subscription {subscription.id} with Stripe data")
                    else:
                        logger.warning(f"No pending subscription found for user {user_id}")
                        
                except Exception as e:
                    logger.error(f"Error processing checkout.session.completed: {str(e)}")

        # ✅ Handle subscription created
        elif event_type == "customer.subscription.created":
            logger.info("Processing customer.subscription.created")
            
            try:
                # Safely handle timestamps
                trial_end = None
                current_period_end = None
                
                if obj.get("trial_end"):
                    trial_end = make_aware(
                        datetime.datetime.fromtimestamp(obj["trial_end"])
                    )
                
                if obj.get("current_period_end"):
                    current_period_end = make_aware(
                        datetime.datetime.fromtimestamp(obj["current_period_end"])
                    )
                
                Subscription.objects.update_or_create(
                    stripe_subscription_id=obj["id"],
                    defaults={
                        "status": obj["status"],
                        "trial_end": trial_end,
                        "current_period_end": current_period_end,
                    },
                )
                logger.info(f"Created/updated subscription for Stripe ID: {obj['id']}")
                
            except Exception as e:
                logger.error(f"Error processing customer.subscription.created: {str(e)}")

        # ✅ Handle subscription updated
        elif event_type == "customer.subscription.updated":
            logger.info("Processing customer.subscription.updated")
            
            try:
                # Safely handle timestamps
                trial_end = None
                current_period_end = None
                
                if obj.get("trial_end"):
                    trial_end = make_aware(
                        datetime.datetime.fromtimestamp(obj["trial_end"])
                    )
                
                if obj.get("current_period_end"):
                    current_period_end = make_aware(
                        datetime.datetime.fromtimestamp(obj["current_period_end"])
                    )
                
                updated_count = Subscription.objects.filter(
                    stripe_subscription_id=obj["id"]
                ).update(
                    status=obj["status"],
                    trial_end=trial_end,
                    current_period_end=current_period_end,
                )
                
                logger.info(f"Updated {updated_count} subscriptions for Stripe ID: {obj['id']}")
                
            except Exception as e:
                logger.error(f"Error processing customer.subscription.updated: {str(e)}")

        # ✅ Handle subscription deleted/cancelled
        elif event_type == "customer.subscription.deleted":
            logger.info("Processing customer.subscription.deleted")
            
            try:
                updated_count = Subscription.objects.filter(
                    stripe_subscription_id=obj["id"]
                ).update(status="canceled")
                
                logger.info(f"Canceled {updated_count} subscriptions for Stripe ID: {obj['id']}")
                
            except Exception as e:
                logger.error(f"Error processing customer.subscription.deleted: {str(e)}")
        
        else:
            logger.info(f"Unhandled webhook event type: {event_type}")

    except Exception as e:
        logger.error(f"Error processing webhook event {event_type}: {str(e)}")
        return HttpResponse(status=500)

    logger.info(f"Webhook processing completed successfully for event: {event_type}")
    return HttpResponse(status=200)