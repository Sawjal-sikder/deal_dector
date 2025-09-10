#!/usr/bin/env python3
"""
Minimal webhook test to identify the specific 500 error
"""
import os
import sys
import django

# Add the project directory to the path
sys.path.append('/home/sawjal/sajal/deal_dector/deal_dector')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.test import RequestFactory
from django.http import HttpRequest
from payment.views import stripe_webhook
import json

def simulate_webhook_request():
    """Simulate a webhook request to identify the error"""
    
    # Create a fake Stripe webhook payload
    fake_payload = {
        "id": "evt_test_123",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_123",
                "subscription": "sub_test_123",
                "metadata": {
                    "user_id": "1",
                    "plan_id": "1"
                }
            }
        }
    }
    
    # Create request
    factory = RequestFactory()
    request = factory.post(
        '/api/payment/webhook/',
        data=json.dumps(fake_payload),
        content_type='application/json'
    )
    
    # Simulate missing Stripe signature (this will cause the error)
    request.META['HTTP_STRIPE_SIGNATURE'] = None
    
    print("🧪 Testing webhook with missing signature...")
    
    try:
        response = stripe_webhook(request)
        print(f"✅ Response status: {response.status_code}")
        return response.status_code == 400  # Expected for missing signature
    except Exception as e:
        print(f"❌ Error in webhook: {e}")
        print(f"Error type: {type(e)}")
        return False

def simulate_valid_webhook():
    """Simulate a valid webhook (but we'll skip Stripe signature verification)"""
    
    # Let's test with a minimal event that should work
    fake_payload = {
        "id": "evt_test_valid",
        "type": "customer.subscription.updated",
        "data": {
            "object": {
                "id": "sub_test_123",
                "status": "active",
                "current_period_end": 1672531200
            }
        }
    }
    
    factory = RequestFactory()
    request = factory.post(
        '/api/payment/webhook/',
        data=json.dumps(fake_payload),
        content_type='application/json'
    )
    
    # Add a fake signature
    request.META['HTTP_STRIPE_SIGNATURE'] = 'fake_signature'
    
    print("🧪 Testing webhook with fake signature (will fail validation)...")
    
    try:
        response = stripe_webhook(request)
        print(f"✅ Response status: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Error in webhook: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Testing webhook function directly...")
    print("=" * 50)
    
    # Test 1: Missing signature
    test1 = simulate_webhook_request()
    print()
    
    # Test 2: Invalid signature  
    test2 = simulate_valid_webhook()
    print()
    
    print("=" * 50)
    print(f"Test 1 (missing sig): {'✅' if test1 else '❌'}")
    print(f"Test 2 (invalid sig): {'✅' if test2 else '❌'}")
