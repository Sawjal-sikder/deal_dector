# 🚀 Payment System Testing with Postman

This guide will help you test all payment endpoints using Postman.

## 🔧 Prerequisites

1. **Django Server Running**: `http://127.0.0.1:8001`
2. **Stripe Account**: Test keys configured in `.env`
3. **User Account**: Create a user account first for authentication

---

## 📋 Postman Collection Setup

### Base URL
```
http://127.0.0.1:8001/api
```

### Environment Variables (in Postman)
Create these variables in your Postman environment:
- `base_url`: `http://127.0.0.1:8001/api`
- `auth_token`: `Bearer YOUR_JWT_TOKEN` (get this from login)
- `user_id`: Your user ID
- `plan_id`: Plan ID you create

---

## 🔐 Step 1: Authentication Setup

### 1.1 Register a User
```http
POST {{base_url}}/auth/register/
Content-Type: application/json

{
    "email": "test@example.com",
    "password": "testpassword123",
    "full_name": "Test User"
}
```

### 1.2 Login to Get JWT Token
```http
POST {{base_url}}/auth/login/
Content-Type: application/json

{
    "email": "test@example.com",
    "password": "testpassword123"
}
```

**Response will contain:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "email": "test@example.com"
    }
}
```

**Copy the `access` token and set it in Postman environment as `auth_token`**

---

## 💰 Step 2: Plan Management

### 2.1 Create a Payment Plan
```http
POST {{base_url}}/payment/plans/
Authorization: {{auth_token}}
Content-Type: application/json

{
    "name": "Monthly Premium Plan",
    "interval": "month",
    "amount": 29.99,
    "trial_days": 7
}
```

**Expected Response:**
```json
{
    "id": 1,
    "name": "Monthly Premium Plan",
    "stripe_product_id": "prod_xxx",
    "stripe_price_id": "price_xxx",
    "amount": 2999,
    "interval": "month",
    "trial_days": 7,
    "active": true
}
```

### 2.2 List All Plans
```http
GET {{base_url}}/payment/plans/
Authorization: {{auth_token}}
```

### 2.3 Update a Plan
```http
PUT {{base_url}}/payment/plans/1/
Authorization: {{auth_token}}
Content-Type: application/json

{
    "name": "Monthly Premium Plan - Updated",
    "amount": 39.99
}
```

---

## 🛒 Step 3: Create Subscription/Payment

### 3.1 Create Subscription (Checkout Session)
```http
POST {{base_url}}/payment/create-subscription/
Authorization: {{auth_token}}
Content-Type: application/json

{
    "plan_id": 1,
    "success_url": "http://localhost:3000/success",
    "cancel_url": "http://localhost:3000/cancel"
}
```

**Expected Response:**
```json
{
    "checkout_url": "https://checkout.stripe.com/pay/cs_test_xxx",
    "session_id": "cs_test_xxx"
}
```

**🔗 Copy the `checkout_url` and open it in your browser to complete the payment**

---

## 📊 Step 4: Check Payment Status

### 4.1 Check Checkout Session Status
```http
POST {{base_url}}/payment/checkout-status/
Authorization: {{auth_token}}
Content-Type: application/json

{
    "session_id": "cs_test_xxx"
}
```

### 4.2 Check User Subscription Status
```http
GET {{base_url}}/payment/subscription-status/
Authorization: {{auth_token}}
```

**Expected Response:**
```json
{
    "has_active_subscription": true,
    "subscription": {
        "id": 1,
        "status": "trialing",
        "plan_name": "Monthly Premium Plan",
        "trial_end": "2025-09-17T12:00:00Z",
        "current_period_end": null
    }
}
```

---

## ✅ Step 5: Payment Success/Cancel Handlers

### 5.1 Payment Success
```http
GET {{base_url}}/payment/payment-success/?session_id=cs_test_xxx
Authorization: {{auth_token}}
```

### 5.2 Payment Cancel
```http
GET {{base_url}}/payment/payment-cancel/
Authorization: {{auth_token}}
```

---

## 🧪 Step 6: Test Stripe Webhook (Optional)

### 6.1 Simulate Webhook Event
```http
POST {{base_url}}/payment/webhook/
Content-Type: application/json
Stripe-Signature: whsec_test_signature

{
    "id": "evt_test_webhook",
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
```

**Note:** This will fail signature verification in production, but you can test the endpoint structure.

---

## 🎯 Complete Postman Collection JSON

Here's a complete Postman collection you can import:

```json
{
    "info": {
        "name": "Deal Detector Payment API",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "item": [
        {
            "name": "Authentication",
            "item": [
                {
                    "name": "Register User",
                    "request": {
                        "method": "POST",
                        "header": [
                            {
                                "key": "Content-Type",
                                "value": "application/json"
                            }
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": "{\n    \"email\": \"test@example.com\",\n    \"password\": \"testpassword123\",\n    \"full_name\": \"Test User\"\n}"
                        },
                        "url": {
                            "raw": "{{base_url}}/auth/register/",
                            "host": ["{{base_url}}"],
                            "path": ["auth", "register", ""]
                        }
                    }
                },
                {
                    "name": "Login User",
                    "request": {
                        "method": "POST",
                        "header": [
                            {
                                "key": "Content-Type",
                                "value": "application/json"
                            }
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": "{\n    \"email\": \"test@example.com\",\n    \"password\": \"testpassword123\"\n}"
                        },
                        "url": {
                            "raw": "{{base_url}}/auth/login/",
                            "host": ["{{base_url}}"],
                            "path": ["auth", "login", ""]
                        }
                    }
                }
            ]
        },
        {
            "name": "Plans",
            "item": [
                {
                    "name": "Create Plan",
                    "request": {
                        "method": "POST",
                        "header": [
                            {
                                "key": "Authorization",
                                "value": "Bearer {{auth_token}}"
                            },
                            {
                                "key": "Content-Type",
                                "value": "application/json"
                            }
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": "{\n    \"name\": \"Monthly Premium Plan\",\n    \"interval\": \"month\",\n    \"amount\": 29.99,\n    \"trial_days\": 7\n}"
                        },
                        "url": {
                            "raw": "{{base_url}}/payment/plans/",
                            "host": ["{{base_url}}"],
                            "path": ["payment", "plans", ""]
                        }
                    }
                },
                {
                    "name": "List Plans",
                    "request": {
                        "method": "GET",
                        "header": [
                            {
                                "key": "Authorization",
                                "value": "Bearer {{auth_token}}"
                            }
                        ],
                        "url": {
                            "raw": "{{base_url}}/payment/plans/",
                            "host": ["{{base_url}}"],
                            "path": ["payment", "plans", ""]
                        }
                    }
                }
            ]
        },
        {
            "name": "Payments",
            "item": [
                {
                    "name": "Create Subscription",
                    "request": {
                        "method": "POST",
                        "header": [
                            {
                                "key": "Authorization",
                                "value": "Bearer {{auth_token}}"
                            },
                            {
                                "key": "Content-Type",
                                "value": "application/json"
                            }
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": "{\n    \"plan_id\": 1,\n    \"success_url\": \"http://localhost:3000/success\",\n    \"cancel_url\": \"http://localhost:3000/cancel\"\n}"
                        },
                        "url": {
                            "raw": "{{base_url}}/payment/create-subscription/",
                            "host": ["{{base_url}}"],
                            "path": ["payment", "create-subscription", ""]
                        }
                    }
                },
                {
                    "name": "Check Subscription Status",
                    "request": {
                        "method": "GET",
                        "header": [
                            {
                                "key": "Authorization",
                                "value": "Bearer {{auth_token}}"
                            }
                        ],
                        "url": {
                            "raw": "{{base_url}}/payment/subscription-status/",
                            "host": ["{{base_url}}"],
                            "path": ["payment", "subscription-status", ""]
                        }
                    }
                }
            ]
        }
    ],
    "variable": [
        {
            "key": "base_url",
            "value": "http://127.0.0.1:8001/api"
        },
        {
            "key": "auth_token",
            "value": "YOUR_JWT_TOKEN_HERE"
        }
    ]
}
```

---

## 🎯 Testing Workflow

1. **Import the collection** into Postman
2. **Set environment variables**:
   - `base_url`: `http://127.0.0.1:8001/api`
3. **Register a new user** (Authentication → Register User)
4. **Login** (Authentication → Login User)
5. **Copy the JWT token** and set it as `auth_token` in environment
6. **Create a plan** (Plans → Create Plan)
7. **Create a subscription** (Payments → Create Subscription)
8. **Open the Stripe checkout URL** in browser to complete payment
9. **Check subscription status** (Payments → Check Subscription Status)

---

## 💳 Stripe Test Card Numbers

Use these test card numbers in Stripe checkout:

- **Success**: `4242424242424242`
- **Decline**: `4000000000000002`
- **Insufficient funds**: `4000000000009995`
- **Expired card**: `4000000000000069`

**Any future expiry date and any 3-digit CVC**

---

## 🔍 Troubleshooting

1. **401 Unauthorized**: Check your JWT token in Authorization header
2. **404 Not Found**: Verify the URL endpoints
3. **500 Internal Server Error**: Check Django server logs
4. **Stripe errors**: Verify your Stripe test keys in `.env`

---

## 📝 Expected Flow

1. User registers/logs in → Gets JWT token
2. Admin creates payment plans → Plans stored in DB + Stripe
3. User selects a plan → Creates Stripe checkout session
4. User completes payment → Stripe webhook updates subscription status
5. User gets access to premium features based on subscription status

This setup allows you to test the complete payment flow from plan creation to subscription management!
