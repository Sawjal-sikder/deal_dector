# 🚀 Quick Payment Testing Guide with Postman

## 📋 **TL;DR - Quick Start**

1. **Start Django Server**: `python manage.py runserver 8001`
2. **Import Postman Collection**: Use the `Deal_Detector_Payment_API.postman_collection.json` file
3. **Set Base URL**: `http://127.0.0.1:8001/api`
4. **Follow the testing sequence** below

---

## 🎯 **Step-by-Step Testing Sequence**

### **Step 1: Authentication**
```http
POST http://127.0.0.1:8001/api/auth/register/
Content-Type: application/json

{
    "email": "test@example.com",
    "password": "testpassword123",
    "full_name": "Test User"
}
```

```http
POST http://127.0.0.1:8001/api/auth/login/
Content-Type: application/json

{
    "email": "test@example.com", 
    "password": "testpassword123"
}
```
**→ Copy the `access` token from response**

### **Step 2: Create Payment Plan**
```http
POST http://127.0.0.1:8001/api/payment/plans/
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json

{
    "name": "Monthly Premium Plan",
    "interval": "month",
    "amount": 29.99,
    "trial_days": 7
}
```
**→ Copy the `id` from response (e.g., plan_id: 1)**

### **Step 3: Create Subscription**
```http
POST http://127.0.0.1:8001/api/payment/create-subscription/
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json

{
    "plan_id": 1,
    "success_url": "http://localhost:3000/success",
    "cancel_url": "http://localhost:3000/cancel"
}
```
**→ Copy the `checkout_url` and open in browser to complete payment**

### **Step 4: Check Status**
```http
GET http://127.0.0.1:8001/api/payment/subscription-status/
Authorization: Bearer YOUR_ACCESS_TOKEN
```

---

## 💳 **Stripe Test Cards**

- **Successful Payment**: `4242424242424242`
- **Payment Declined**: `4000000000000002`
- **Insufficient Funds**: `4000000000009995`

**Use any future expiry date (e.g., 12/25) and any 3-digit CVC (e.g., 123)**

---

## 📁 **Files Created for You**

1. **`POSTMAN_PAYMENT_TESTING_GUIDE.md`** - Detailed testing guide
2. **`Deal_Detector_Payment_API.postman_collection.json`** - Ready-to-import Postman collection

### **To Import in Postman:**
1. Open Postman
2. Click "Import" button
3. Select `Deal_Detector_Payment_API.postman_collection.json`
4. Set environment variable `base_url` = `http://127.0.0.1:8001/api`

---

## 🔧 **Available Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register/` | Register new user |
| `POST` | `/auth/login/` | Login user |
| `GET` | `/payment/plans/` | List all plans |
| `POST` | `/payment/plans/` | Create new plan |
| `PUT` | `/payment/plans/{id}/` | Update plan |
| `POST` | `/payment/create-subscription/` | Create subscription |
| `GET` | `/payment/subscription-status/` | Check user subscription |
| `POST` | `/payment/checkout-status/` | Check checkout session |
| `GET` | `/payment/payment-success/` | Handle successful payment |
| `GET` | `/payment/payment-cancel/` | Handle payment cancellation |
| `POST` | `/payment/webhook/` | Stripe webhook handler |

---

## 🔍 **Testing Workflow**

1. **Register/Login** → Get JWT token
2. **Create Plan** → Get plan_id
3. **Create Subscription** → Get checkout_url
4. **Complete Payment** → Use Stripe test cards
5. **Check Status** → Verify subscription is active

---

## ⚡ **Quick Commands**

**Start Server:**
```bash
cd /home/sawjal/sajal/deal_dector/deal_dector
source ../venv/bin/activate
python manage.py runserver 8001
```

**Test Endpoint:**
```bash
curl -X GET http://127.0.0.1:8001/api/payment/plans/ \
  -H "Content-Type: application/json"
```

---

## 🎯 **Expected Flow**

1. **User Registration** → Creates user account
2. **Plan Creation** → Creates Stripe product + price
3. **Subscription Creation** → Creates Stripe checkout session
4. **Payment Completion** → Webhook updates subscription status
5. **Status Check** → Returns active subscription details

---

## 🚨 **Common Issues & Solutions**

| Issue | Solution |
|-------|----------|
| **401 Unauthorized** | Add `Authorization: Bearer TOKEN` header |
| **404 Not Found** | Check URL - should be `http://127.0.0.1:8001/api/...` |
| **500 Internal Server Error** | Check Django server logs |
| **Connection Refused** | Ensure Django server is running on port 8001 |
| **Stripe Error** | Verify Stripe test keys in `.env` file |

---

## 🎉 **Ready to Test!**

Your payment system is fully configured and ready for testing. The webhook issues have been fixed, and all endpoints should work properly.

**Next Steps:**
1. Start the Django server
2. Import the Postman collection
3. Follow the testing sequence
4. Complete a test payment with Stripe test cards

Happy testing! 🚀
