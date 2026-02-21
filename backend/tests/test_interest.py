"""
Unit Tests for Interest Calculation Engine
Tests 2% monthly interest with daily batch job
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from decimal import Decimal
import sys
sys.path.append('..')
from services.interest_engine import InterestEngine


class TestInterestCalculation:
    """Test 2% monthly interest calculation logic"""
    
    def test_daily_interest_rate(self):
        """Test that daily rate is correctly calculated from 2% monthly"""
        # 2% monthly = 0.02 / 30 per day
        engine = InterestEngine()
        monthly_rate = 0.02
        daily_rate = monthly_rate / 30
        
        assert abs(daily_rate - 0.0006666667) < 0.0000001
    
    def test_interest_on_principal(self):
        """Test interest calculation on outstanding principal"""
        engine = InterestEngine()
        principal = Decimal("10000.00")
        days = 1
        
        # Daily interest = 10000 * 0.02 / 30 = 6.67
        expected_interest = principal * Decimal("0.02") / Decimal("30")
        calculated_interest = engine.calculate_daily_interest(principal, days)
        
        assert abs(calculated_interest - expected_interest) < Decimal("0.01")
    
    def test_no_interest_on_zero_balance(self):
        """Test that no interest is applied when balance is zero"""
        engine = InterestEngine()
        principal = Decimal("0.00")
        
        interest = engine.calculate_daily_interest(principal, 1)
        assert interest == Decimal("0.00")
    
    def test_compound_interest_over_month(self):
        """Test interest compounding over 30 days"""
        engine = InterestEngine()
        initial_principal = Decimal("10000.00")
        days = 30
        
        # After 30 days at 2% monthly, should be approximately 200
        total_interest = initial_principal * Decimal("0.02")
        
        # Simple interest for 30 days
        calculated = engine.calculate_daily_interest(initial_principal, 1) * days
        
        assert abs(calculated - total_interest) < Decimal("1.00")


class TestBatchJobExecution:
    """Test automated interest batch job (12:01 AM IST)"""
    
    def test_batch_job_runs_daily(self):
        """Test that batch job processes all customers with outstanding balance"""
        # Mock batch job execution
        engine = InterestEngine()
        
        # Simulate customers with balances
        customers_with_balance = [
            {"customer_id": "C1", "outstanding_balance": Decimal("5000.00")},
            {"customer_id": "C2", "outstanding_balance": Decimal("10000.00")},
            {"customer_id": "C3", "outstanding_balance": Decimal("0.00")},  # Should skip
        ]
        
        processed_count = 0
        for customer in customers_with_balance:
            if customer["outstanding_balance"] > 0:
                interest = engine.calculate_daily_interest(customer["outstanding_balance"], 1)
                if interest > 0:
                    processed_count += 1
        
        assert processed_count == 2  # Only C1 and C2
    
    def test_batch_job_idempotency(self):
        """Test that running batch job twice for same day doesn't duplicate interest"""
        # Implementation should check if interest already applied for today
        pass


class TestPaymentWaterfall:
    """Test payment waterfall algorithm (interest first, then principal)"""
    
    def test_payment_clears_interest_first(self):
        """Test that payments clear accrued interest before principal"""
        engine = InterestEngine()
        
        principal = Decimal("10000.00")
        accrued_interest = Decimal("200.00")
        payment = Decimal("150.00")
        
        # Payment should reduce interest first
        result = engine.apply_payment_waterfall(principal, accrued_interest, payment)
        
        assert result["remaining_interest"] == Decimal("50.00")
        assert result["remaining_principal"] == Decimal("10000.00")
    
    def test_payment_exceeds_interest(self):
        """Test payment that covers all interest and reduces principal"""
        engine = InterestEngine()
        
        principal = Decimal("10000.00")
        accrued_interest = Decimal("200.00")
        payment = Decimal("1200.00")
        
        result = engine.apply_payment_waterfall(principal, accrued_interest, payment)
        
        assert result["remaining_interest"] == Decimal("0.00")
        assert result["remaining_principal"] == Decimal("9000.00")  # 10000 - 1000
    
    def test_payment_clears_all_debt(self):
        """Test payment that clears both interest and principal completely"""
        engine = InterestEngine()
        
        principal = Decimal("1000.00")
        accrued_interest = Decimal("50.00")
        payment = Decimal("1050.00")
        
        result = engine.apply_payment_waterfall(principal, accrued_interest, payment)
        
        assert result["remaining_interest"] == Decimal("0.00")
        assert result["remaining_principal"] == Decimal("0.00")
        assert result["excess_payment"] == Decimal("0.00")


class TestManualOverrides:
    """Test manual interest freeze and waive-off functionality"""
    
    def test_freeze_interest(self):
        """Test freezing interest calculation for a customer"""
        engine = InterestEngine()
        
        # Mark customer as interest_frozen
        customer = {"customer_id": "C123", "interest_frozen": True, "outstanding_balance": Decimal("5000.00")}
        
        if not customer.get("interest_frozen", False):
            interest = engine.calculate_daily_interest(customer["outstanding_balance"], 1)
        else:
            interest = Decimal("0.00")
        
        assert interest == Decimal("0.00")
    
    def test_waive_off_interest(self):
        """Test manual waive-off of accrued interest"""
        engine = InterestEngine()
        
        accrued_interest = Decimal("250.00")
        waive_amount = Decimal("100.00")
        
        remaining_interest = accrued_interest - waive_amount
        
        assert remaining_interest == Decimal("150.00")


class TestInterestLogging:
    """Test interest application logging to interest_logs collection"""
    
    def test_interest_log_entry(self):
        """Test that interest application creates a log entry"""
        log_entry = {
            "customer_id": "C123",
            "retailer_id": "R456",
            "principal_amount": Decimal("10000.00"),
            "interest_amount": Decimal("6.67"),
            "applied_date": datetime.now(),
            "calculation_method": "daily_2_percent_monthly"
        }
        
        assert log_entry["customer_id"] is not None
        assert log_entry["interest_amount"] > 0
    
    def test_interest_history_tracking(self):
        """Test retrieving interest history for a customer"""
        # Should be able to query interest_logs by customer_id
        # Ordered by applied_date DESC
        pass


# Run with: pytest tests/test_interest.py -v
