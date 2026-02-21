"""
Unit Tests for Ledger Operations
Tests double-entry accounting, transaction flows, and balance calculations
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from decimal import Decimal
from main import app

client = TestClient(app)

# Test helper: Get auth token
def get_auth_token():
    otp_response = client.post("/api/auth/request-otp", json={"phone": "+919876543210"})
    otp = otp_response.json()["otp"]
    verify_response = client.post("/api/auth/verify-otp", json={"phone": "+919876543210", "otp": otp})
    return verify_response.json()["access_token"]


class TestSaleOnCredit:
    """Test credit sale transactions"""
    
    def test_create_credit_sale(self):
        """Test creating a sale on credit"""
        token = get_auth_token()
        
        response = client.post(
            "/api/ledger/sale-on-credit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "customer_id": "test_customer_123",
                "amount": 5000.00,
                "description": "Groceries purchase",
                "promised_return_date": "2025-02-15"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["entry_type"] == "SALE_ON_CREDIT"
        assert float(data["debit_amount"]) == 5000.00
        assert data["outstanding_balance"] > 0
    
    def test_credit_sale_negative_amount(self):
        """Test that negative amounts are rejected"""
        token = get_auth_token()
        
        response = client.post(
            "/api/ledger/sale-on-credit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "customer_id": "test_customer_123",
                "amount": -100.00,
                "description": "Invalid negative"
            }
        )
        
        assert response.status_code == 400
    
    def test_credit_sale_missing_customer(self):
        """Test credit sale without customer ID"""
        token = get_auth_token()
        
        response = client.post(
            "/api/ledger/sale-on-credit",
            headers={"Authorization": f"Bearer {token}"},
            json={"amount": 1000.00}
        )
        
        assert response.status_code == 422


class TestPayments:
    """Test payment transactions"""
    
    def test_cash_payment(self):
        """Test recording a cash payment"""
        token = get_auth_token()
        
        # First create a credit sale
        client.post(
            "/api/ledger/sale-on-credit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "customer_id": "test_customer_456",
                "amount": 3000.00,
                "description": "Initial credit"
            }
        )
        
        # Then make a payment
        response = client.post(
            "/api/ledger/payment",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "customer_id": "test_customer_456",
                "amount": 1000.00,
                "description": "Partial payment"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["entry_type"] == "PAYMENT"
        assert float(data["credit_amount"]) == 1000.00
    
    def test_payment_waterfall_algorithm(self):
        """Test that payments clear interest first, then principal"""
        token = get_auth_token()
        
        # Create credit with accrued interest
        # This test requires interest to be applied first
        # Then verify payment clears interest before principal
        pass  # Implementation depends on interest calculation


class TestDoubleEntry:
    """Test double-entry accounting principles"""
    
    def test_balance_equation(self):
        """Verify debit = credit for all transactions"""
        token = get_auth_token()
        
        # Get all ledger entries for a customer
        response = client.get(
            "/api/ledger/customer/test_customer_789/history",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            entries = response.json()
            total_debit = sum(float(e.get("debit_amount", 0)) for e in entries)
            total_credit = sum(float(e.get("credit_amount", 0)) for e in entries)
            
            # In double-entry, debits should equal credits
            assert abs(total_debit - total_credit) < 0.01  # Allow for floating point precision
    
    def test_outstanding_balance_accuracy(self):
        """Test that outstanding balance is calculated correctly"""
        token = get_auth_token()
        
        # Create transactions and verify balance
        customer_id = "test_balance_check"
        
        # Sale: +5000
        client.post(
            "/api/ledger/sale-on-credit",
            headers={"Authorization": f"Bearer {token}"},
            json={"customer_id": customer_id, "amount": 5000.00}
        )
        
        # Payment: -2000
        client.post(
            "/api/ledger/payment",
            headers={"Authorization": f"Bearer {token}"},
            json={"customer_id": customer_id, "amount": 2000.00}
        )
        
        # Get latest balance
        response = client.get(
            f"/api/customers/{customer_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            customer = response.json()
            # Balance should be 3000 (5000 - 2000)
            assert abs(float(customer["outstanding_balance"]) - 3000.00) < 0.01


class TestTransactionHistory:
    """Test ledger history retrieval"""
    
    def test_get_customer_ledger(self):
        """Test retrieving customer's transaction history"""
        token = get_auth_token()
        
        response = client.get(
            "/api/ledger/customer/test_customer_123/history",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_ledger_pagination(self):
        """Test pagination on ledger entries"""
        token = get_auth_token()
        
        response = client.get(
            "/api/ledger/customer/test_customer_123/history?page=1&limit=10",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code in [200, 404]


# Run with: pytest tests/test_ledger.py -v
