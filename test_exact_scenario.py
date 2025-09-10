#!/usr/bin/env python3
"""
Test the exact webhook scenario that's failing
"""
import os
import sys
import django

# Add the project directory to the path
sys.path.append('/home/sawjal/sajal/deal_dector/deal_dector')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

import stripe
from payment.models import Subscription
from django.contrib.auth import get_user_model

User = get_user_model()

# Set Stripe API key
stripe.api_key = os.getenv("STRIPE_API_KEY")

def test_webhook_scenario():
    """Test the exact scenario from the latest webhook"""
    
    user_id = "20"
    subscription_id = "sub_1S5gqdGazRNopHIjCxd3tuL0"
    
    print(f"🧪 Testing webhook scenario:")
    print(f"  User ID: {user_id}")
    print(f"  Stripe Subscription ID: {subscription_id}")
    
    # Step 1: Check if user exists
    try:
        user = User.objects.get(id=user_id)
        print(f"✅ User found: {user.email}")
    except User.DoesNotExist:
        print("❌ User not found")
        return False
    
    # Step 2: Check pending subscriptions
    pending_subs = Subscription.objects.filter(
        user_id=user_id,
        status="pending"
    )
    print(f"📊 Found {pending_subs.count()} pending subscriptions")
    
    if pending_subs.count() == 0:
        print("❌ No pending subscription found")
        return False
    elif pending_subs.count() > 1:
        print("⚠️  Multiple pending subscriptions found - this could cause issues")
        for i, sub in enumerate(pending_subs):
            print(f"     {i+1}. Subscription {sub.id} - Plan: {sub.plan.name if sub.plan else 'None'}")
    
    # Step 3: Try to retrieve subscription from Stripe
    print(f"🔍 Attempting to retrieve Stripe subscription: {subscription_id}")
    try:
        stripe_subscription = stripe.Subscription.retrieve(subscription_id)
        print(f"✅ Stripe subscription retrieved successfully")
        print(f"   Status: {stripe_subscription.status}")
        print(f"   Trial end: {stripe_subscription.trial_end}")
        print(f"   Current period end: {stripe_subscription.current_period_end}")
    except stripe.error.InvalidRequestError as e:
        print(f"❌ Stripe API error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error retrieving from Stripe: {e}")
        return False
    
    # Step 4: Try to update the first pending subscription
    try:
        subscription = pending_subs.first()
        print(f"🔄 Attempting to update subscription {subscription.id}")
        
        subscription.stripe_subscription_id = stripe_subscription.id
        subscription.status = stripe_subscription.status
        
        # Handle timestamps safely
        from django.utils.timezone import make_aware
        import datetime
        
        if stripe_subscription.trial_end:
            subscription.trial_end = make_aware(
                datetime.datetime.fromtimestamp(stripe_subscription.trial_end)
            )
        
        if stripe_subscription.current_period_end:
            subscription.current_period_end = make_aware(
                datetime.datetime.fromtimestamp(stripe_subscription.current_period_end)
            )
        
        subscription.save()
        print(f"✅ Subscription updated successfully")
        print(f"   Status: {subscription.status}")
        print(f"   Stripe ID: {subscription.stripe_subscription_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating subscription: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Testing exact webhook failure scenario...")
    print("=" * 60)
    
    success = test_webhook_scenario()
    
    print("=" * 60)
    print(f"Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
    
    if not success:
        print("\n💡 Potential fixes:")
        print("1. Clean up duplicate pending subscriptions")
        print("2. Check Stripe subscription status")
        print("3. Verify database constraints")
        print("4. Add better error handling in webhook")
