from django.urls import path
from .views import *

urlpatterns = [
      path("create-subscription/", CreateSubscriptionView.as_view(), name="create-subscription"),
      path("payment-success/", PaymentSuccessView.as_view(), name="payment-success"),
      path("payment-cancel/", PaymentCancelView.as_view(), name="payment-cancel"),
      path("checkout-status/", CheckoutSessionStatusView.as_view(), name="checkout-status"),
      path("subscription-status/", UserSubscriptionStatusView.as_view(), name="subscription-status"),
      path("webhook/", stripe_webhook, name="stripe-webhook"),
      path("plans/", PlanListCreateView.as_view(), name="plan-list-create"),
      path("plans/<int:id>/", PlanUpdateView.as_view(), name="plan-update"),

]
