from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class InterestCalculationEngine:
    """
    The Automated Interest & Penalty Engine
    
    Implements the 2% monthly interest calculation logic with:
    - Daily accrual calculations
    - Interest freezing capability
    - Partial payment waterfall allocation
    - NPA (Non-Performing Asset) handling
    """
    
    MONTHLY_INTEREST_RATE = 0.02  # 2% per month
    DAILY_INTEREST_RATE = MONTHLY_INTEREST_RATE / 30  # ~0.0667% per day
    
    @staticmethod
    def calculate_daily_interest(principal: float) -> float:
        """
        Calculate daily interest based on principal amount.
        Formula: (Principal * 0.02) / 30
        
        Example: If principal is ₹5,000
        Daily Interest = (5000 * 0.02) / 30 = ₹3.33
        """
        return (principal * InterestCalculationEngine.DAILY_INTEREST_RATE)
    
    @staticmethod
    def calculate_interest_for_period(principal: float, days_overdue: int) -> float:
        """
        Calculate total interest accrued for a specific number of days.
        
        Args:
            principal: Outstanding principal amount
            days_overdue: Number of days past the promised return date
            
        Returns:
            Total interest accrued for the period
        """
        daily_interest = InterestCalculationEngine.calculate_daily_interest(principal)
        return round(daily_interest * days_overdue, 2)
    
    @staticmethod
    def is_overdue(promised_return_date: datetime) -> bool:
        """
        Check if a transaction is overdue.
        
        Args:
            promised_return_date: The promised date for return/payment
            
        Returns:
            True if the current date is past the promised date
        """
        if promised_return_date is None:
            return False
        return datetime.utcnow() > promised_return_date
    
    @staticmethod
    def calculate_days_overdue(promised_return_date: datetime) -> int:
        """
        Calculate the number of days a transaction is overdue.
        
        Args:
            promised_return_date: The promised date for return/payment
            
        Returns:
            Number of days overdue (0 if not yet due)
        """
        if promised_return_date is None:
            return 0
        
        days_diff = (datetime.utcnow() - promised_return_date).days
        return max(0, days_diff)
    
    @staticmethod
    def allocate_payment_waterfall(total_payment: float, accrued_interest: float, 
                                 principal_outstanding: float) -> Tuple[float, float]:
        """
        Allocate incoming payment using the Waterfall Method:
        1. First clear any accrued interest
        2. Apply remaining payment to principal reduction
        
        Args:
            total_payment: Total payment amount received
            accrued_interest: Currently accrued interest (if any)
            principal_outstanding: Outstanding principal amount
            
        Returns:
            Tuple of (interest_paid, principal_paid)
            
        Example:
            Customer owes ₹10,000 (Principal) + ₹500 (Interest)
            They pay ₹2,000
            
            Step 1: Pay ₹500 interest
            Step 2: Apply remaining ₹1,500 to principal
            
            Result: (500, 1500)
        """
        interest_paid = min(total_payment, accrued_interest)
        principal_paid = total_payment - interest_paid
        
        return (round(interest_paid, 2), round(principal_paid, 2))
    
    @staticmethod
    def generate_batch_interest_entries(accounts_data: List[Dict]) -> List[Dict]:
        """
        Batch processing logic for the nightly interest calculation.
        
        This is the heart of the automated batch job that runs at 12:01 AM.
        
        Args:
            accounts_data: List of account dictionaries with:
                - account_id
                - principal_outstanding
                - promised_return_date
                - freeze_interest (boolean)
                - last_interest_calc_date (optional for handling gaps)
                
        Returns:
            List of interest entry dictionaries ready to be inserted into the database
        """
        interest_entries = []
        
        for account in accounts_data:
            # Skip if principal is 0 or frozen
            if account.get('principal_outstanding', 0) <= 0:
                continue
            
            if account.get('freeze_interest', False):
                logger.info(f"Skipping interest calculation for account {account['account_id']}: Interest frozen")
                continue
            
            # Check if account is overdue
            if not InterestCalculationEngine.is_overdue(account.get('promised_return_date')):
                continue
            
            # Calculate days since last interest calculation
            last_calc_date = account.get('last_interest_calc_date')
            if last_calc_date:
                days_since_calc = (datetime.utcnow() - last_calc_date).days
            else:
                days_since_calc = 1
            
            # Calculate interest
            principal = account['principal_outstanding']
            daily_interest = InterestCalculationEngine.calculate_daily_interest(principal)
            total_interest_for_period = round(daily_interest * days_since_calc, 2)
            
            if total_interest_for_period > 0:
                interest_entry = {
                    'account_id': account['account_id'],
                    'transaction_type': 'interest_applied',
                    'amount': total_interest_for_period,
                    'calculation_date': datetime.utcnow(),
                    'principal_at_time': principal,
                    'days_calculated': days_since_calc,
                    'entry_type': 'DR',  # Debit (increases customer's debt)
                }
                interest_entries.append(interest_entry)
                logger.info(f"Interest entry for account {account['account_id']}: ₹{total_interest_for_period}")
        
        return interest_entries
    
    @staticmethod
    def calculate_npa_writeoff(account_id: str, remaining_amount: float) -> Dict:
        """
        Create an NPA (Non-Performing Asset) write-off entry.
        
        When the shop owner decides to write off a bad debt completely,
        this creates the necessary double-entry transactions:
        
        Debit: Bad Debt Expense
        Credit: Customer Account (clears their debt)
        
        Args:
            account_id: The account being written off
            remaining_amount: The amount to write off
            
        Returns:
            Dictionary with write-off transaction details
        """
        return {
            'transaction_type': 'npa_writeoff',
            'account_id': account_id,
            'amount': remaining_amount,
            'writeoff_date': datetime.utcnow(),
            'entries': [
                {
                    'account_id': account_id,
                    'entry_type': 'CR',  # Credit (clears customer debt)
                    'amount': remaining_amount,
                },
                {
                    'account_id': 'internal_bad_debt_expense',
                    'entry_type': 'DR',  # Debit (records expense)
                    'amount': remaining_amount,
                }
            ]
        }


class BatchJobScheduler:
    """
    Manages the scheduled batch job for interest calculation.
    
    In production, this would be triggered by a cron job at 12:01 AM daily.
    For development, it can be triggered via an API endpoint.
    """
    
    @staticmethod
    def run_daily_interest_batch(db_connection) -> Dict:
        """
        Execute the daily interest calculation batch job.
        
        Process:
        1. Query all accounts with outstanding balance
        2. Filter for accounts past promised return date
        3. Calculate interest for each
        4. Insert interest entries
        5. Update account roll-ups
        6. Generate report
        
        Args:
            db_connection: Database connection object
            
        Returns:
            Batch job execution report
        """
        report = {
            'job_start_time': datetime.utcnow(),
            'accounts_processed': 0,
            'interest_entries_created': 0,
            'total_interest_applied': 0.0,
            'errors': [],
        }
        
        try:
            # Query scope: accounts with outstanding balance and overdue
            accounts_collection = db_connection['customer_accounts']
            overdue_accounts = list(accounts_collection.find({
                'total_outstanding': {'$gt': 0},
                'promised_return_date': {'$lt': datetime.utcnow()},
                'is_active': True
            }))
            
            # Generate interest entries
            interest_entries = InterestCalculationEngine.generate_batch_interest_entries(overdue_accounts)
            
            report['accounts_processed'] = len(overdue_accounts)
            report['interest_entries_created'] = len(interest_entries)
            report['total_interest_applied'] = sum(e['amount'] for e in interest_entries)
            
            # Insert entries (in production)
            # ledger_entries_collection = db_connection['ledger_entries']
            # if interest_entries:
            #     ledger_entries_collection.insert_many(interest_entries)
            
            report['job_end_time'] = datetime.utcnow()
            report['status'] = 'completed'
            
            logger.info(f"Batch job completed: {report}")
            
        except Exception as e:
            report['status'] = 'failed'
            report['errors'].append(str(e))
            logger.error(f"Batch job failed: {str(e)}")
        
        return report
