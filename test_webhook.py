#!/usr/bin/env python3
"""
Test script to debug webhook issues
"""
import os
import sys
import django

# Add the project directory to the path
sys.path.append('/home/sawjal/sajal/deal_dector/deal_dector')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

import json
import requests
import stripe
from payment.models import WebhookEvent

# Test data for different webhook scenarios
test_webhook_events = {
    'checkout_session_completed': {
        "id": "evt_test_webhook",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_123",
                "object": "checkout.session",
                "subscription": "sub_test_123",
                "metadata": {
                    "user_id": "1",
                    "plan_id": "1"
                }
            }
        }
    },
    'subscription_created': {
        "id": "evt_test_webhook_2",
        "type": "customer.subscription.created",
        "data": {
            "object": {
                "id": "sub_test_123",
                "object": "subscription",
                "status": "trialing",
                "trial_end": 1672531200,  # Jan 1, 2023
                "current_period_end": 1675209600  # Feb 1, 2023
            }
        }
    }
}

def test_webhook_endpoint():
    """Test the webhook endpoint directly"""
    print("🔍 Testing webhook endpoint...")
    
    # Test basic connectivity
    try:
        response = requests.get('http://127.0.0.1:8001/api/payment/webhook/')
        print(f"GET request status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure Django server is running on port 8001")
        return False
    
    # Test POST with invalid data (should get 400)
    try:
        response = requests.post(
            'http://127.0.0.1:8001/api/payment/webhook/',
            json={"test": "data"},
            headers={'Content-Type': 'application/json'}
        )
        print(f"POST with test data status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing POST: {e}")
        return False
    
    return True

def check_environment():
    """Check if environment variables are set"""
    print("🔍 Checking environment variables...")
    
    stripe_key = os.getenv("STRIPE_API_KEY")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    print(f"STRIPE_API_KEY: {'✅ Set' if stripe_key else '❌ Missing'}")
    print(f"STRIPE_WEBHOOK_SECRET: {'✅ Set' if webhook_secret else '❌ Missing'}")
    
    if stripe_key:
        print(f"STRIPE_API_KEY starts with: {stripe_key[:10]}...")
    if webhook_secret:
        print(f"STRIPE_WEBHOOK_SECRET starts with: {webhook_secret[:10]}...")
    
    return bool(stripe_key and webhook_secret)

def check_database():
    """Check database connectivity"""
    print("🔍 Checking database...")
    
    try:
        # Try to count WebhookEvent objects
        count = WebhookEvent.objects.count()
        print(f"✅ Database accessible. Current webhook events: {count}")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def main():
    print("🚀 Starting webhook debugging...")
    print("=" * 50)
    
    # Run checks
    env_ok = check_environment()
    db_ok = check_database()
    server_ok = test_webhook_endpoint()
    
    print("\n" + "=" * 50)
    print("📊 Summary:")
    print(f"Environment: {'✅' if env_ok else '❌'}")
    print(f"Database: {'✅' if db_ok else '❌'}")
    print(f"Server: {'✅' if server_ok else '❌'}")
    
    if not env_ok:
        print("\n❌ Environment issues detected. Check your .env file.")
    
    if not db_ok:
        print("\n❌ Database issues detected. Run migrations if needed.")
        
    if not server_ok:
        print("\n❌ Server issues detected. Make sure Django is running.")
    
    if env_ok and db_ok and server_ok:
        print("\n✅ All checks passed! Webhook should be working.")
    
    print("\n🔍 Recent webhook events:")
    try:
        recent_events = WebhookEvent.objects.order_by('-received_at')[:5]
        if recent_events:
            for event in recent_events:
                print(f"  - {event.type} ({event.event_id}) at {event.received_at}")
        else:
            print("  No recent webhook events found.")
    except Exception as e:
        print(f"  Error fetching events: {e}")

if __name__ == "__main__":
    main()
