# Bahi-Khata Digital API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
All API endpoints (except `/` and `/health`) require JWT authentication via the `Authorization` header:
```
Authorization: Bearer <access_token>
```

## API Endpoints

### 1. Authentication (`/api/v1/auth`)

#### Register User
```
POST /api/v1/auth/register
Content-Type: application/json

Request:
{
  "phone_number": "9876543210",
  "pin": "1234",
  "shop_name": "राज किराना",
  "owner_name": "राज कुमार",
  "address": "मुख्य बाजार, पुणे"
}

Response: 201 Created
{
  "message": "User registered successfully",
  "user_id": "507f1f77bcf86cd799439011"
}
```

#### Login
```
POST /api/v1/auth/login
Content-Type: application/json

Request:
{
  "phone_number": "9876543210",
  "pin": "1234"
}

Response: 200 OK
{
  "access_token": "eyJ0eXAiOiJKV1QiLC...",
  "token_type": "bearer",
  "user_id": "507f1f77bcf86cd799439011",
  "shop_name": "राज किराना"
}
```

### 2. Customers (`/api/v1/customers`)

#### Create Customer
```
POST /api/v1/customers
Authorization: Bearer <token>
Content-Type: application/json

Request:
{
  "name": "हरि प्रसाद",
  "father_name": "रवि प्रसाद",
  "phone_number": "9876543210",
  "village_ward": "भारतपुर वार्ड 5",
  "address": "मुख्य बाजार, भारतपुर",
  "aadhaar_number": "123456789012",
  "credit_limit": 50000.00
}

Response: 201 Created
{
  "_id": "507f1f77bcf86cd799439012",
  "name": "हरि प्रसाद",
  "outstanding_balance": 0,
  "risk_category": "Excellent"
}
```

#### Get All Customers
```
GET /api/v1/customers
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "_id": "507f1f77bcf86cd799439012",
    "name": "हरि प्रसाद",
    "outstanding_balance": 5000,
    "risk_category": "Average"
  }
]
```

#### Get Customer Details
```
GET /api/v1/customers/{customer_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "_id": "507f1f77bcf86cd799439012",
  "name": "हरि प्रसाद",
  "father_name": "रवि प्रसाद",
  "phone_number": "9876543210",
  "outstanding_balance": 5000,
  "outstanding_interest": 25.50,
  "promised_return_date": "2026-03-15",
  "risk_category": "Average"
}
```

### 3. Ledger Transactions (`/api/v1/ledger`)

#### Create Sale on Credit
```
POST /api/v1/ledger/sale-on-credit
Authorization: Bearer <token>
Content-Type: application/json

Request:
{
  "customer_id": "507f1f77bcf86cd799439012",
  "items": [
    {
      "name": "Rice 10kg",
      "quantity": 1,
      "price": 500,
      "amount": 500
    }
  ],
  "total_amount": 500,
  "promised_return_date": "2026-03-15",
  "notes": "ईद के लिए चावल"
}

Response: 201 Created
{
  "transaction_id": "TX-2026-02-21-001",
  "customer_id": "507f1f77bcf86cd799439012",
  "amount": 500,
  "type": "Sale_on_Credit",
  "outstanding_balance": 5500
}
```

#### Create Payment
```
POST /api/v1/ledger/payment
Authorization: Bearer <token>
Content-Type: application/json

Request:
{
  "customer_id": "507f1f77bcf86cd799439012",
  "amount_paid": 1000,
  "payment_method": "cash",
  "notes": "आधा रुपये दिया गया"
}

Response: 201 Created
{
  "transaction_id": "TX-2026-02-21-002",
  "amount_paid": 1000,
  "outstanding_balance": 4500,
  "interest_cleared": 25.50,
  "principal_cleared": 974.50
}
```

### 4. Analytics & Dashboard (`/api/v1/analytics`)

#### Get Dashboard Summary
```
GET /api/v1/analytics/dashboard/summary
Authorization: Bearer <token>

Response: 200 OK
{
  "total_outstanding": 150000,
  "total_collections": 25000,
  "total_accounts": 45,
  "active_accounts": 42,
  "pending_interest_charges": 3500,
  "npa_amount": 5000
}
```

#### Get Village-wise Breakdown
```
GET /api/v1/analytics/village-wise?start_date=2026-01-01&end_date=2026-02-21
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "village": "भारतपुर",
    "total_outstanding": 85000,
    "account_count": 25,
    "collection_percentage": 75
  }
]
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request format"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid or missing authentication token"
}
```

### 404 Not Found
```json
{
  "detail": "Customer not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "An unexpected error occurred"
}
```

## Batch Job
Daily interest calculation runs at **12:01 AM IST** automatically.
- Calculates: (Outstanding_Principal * 0.02) / 30
- Posts automatic interest transaction
- Updates customer outstanding balance

## Rate Limiting
No rate limiting currently. Recommended: Implement rate limiting at 1000 requests/hour per user.

## Pagination (Future)
All list endpoints will support pagination with `?page=1&limit=20` parameters.

## Interactive API Documentation
Access Swagger UI at: `http://localhost:8000/docs`
Access ReDoc at: `http://localhost:8000/redoc`
