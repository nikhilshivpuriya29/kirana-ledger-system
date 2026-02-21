from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from decimal import Decimal
import logging
from database import db, COLLECTIONS
from services.interest_engine import InterestCalculationEngine

logger = logging.getLogger(__name__)

class BatchJobScheduler:
    """Manages APScheduler for automated batch jobs like daily interest calculation"""
    
    scheduler: AsyncIOScheduler = None
    
    @staticmethod
    def initialize_scheduler():
        """Initialize AsyncIO scheduler with batch jobs"""
        BatchJobScheduler.scheduler = AsyncIOScheduler()
        
        # Schedule daily interest calculation at 12:01 AM IST (+5:30)
        # Convert IST to UTC: 12:01 AM IST = 6:31 PM UTC previous day
        BatchJobScheduler.scheduler.add_job(
            BatchJobScheduler.run_daily_interest_calculation,
            CronTrigger(hour=18, minute=31, timezone='UTC'),
            id='daily_interest_calc',
            name='Daily Interest Calculation (12:01 AM IST)',
            misfire_grace_time=600,  # Allow 10 minutes grace period
        )
        
        BatchJobScheduler.scheduler.start()
        logger.info("Batch scheduler initialized successfully")
    
    @staticmethod
    async def run_daily_interest_calculation():
        """Daily batch job to calculate and post interest for all active accounts"""
        try:
            logger.info("Starting daily interest calculation batch job")
            db_instance = db.get_database()
            customers_col = db_instance[COLLECTIONS['customers']]
            transactions_col = db_instance[COLLECTIONS['transactions']]
            
            today = datetime.utcnow().date()
            
            # Find all customers with outstanding balance and no frozen interest
            active_accounts = customers_col.find({
                'outstanding_balance': {'$gt': 0},
                'freeze_interest': False,
                'promised_date': {'$lt': datetime.combine(today, datetime.min.time())},
                'is_active': True
            })
            
            processed_count = 0
            errors = []
            
            for customer in active_accounts:
                try:
                    principal = Decimal(str(customer.get('outstanding_balance', 0)))
                    interest_amount = InterestCalculationEngine.calculate_daily_interest(float(principal))
                    
                    if interest_amount > 0:
                        # Create interest transaction
                        interest_transaction = {
                            'user_id': customer['user_id'],
                            'customer_id': str(customer['_id']),
                            'transaction_type': 'Interest_Applied',
                            'amount': interest_amount,
                            'description': f'Daily Interest - {today.strftime("%d-%m-%Y")}',
                            'created_at': datetime.utcnow(),
                            'created_by_system': True,
                            'batch_job_id': 'daily_interest_calc'
                        }
                        
                        transactions_col.insert_one(interest_transaction)
                        processed_count += 1
                        
                except Exception as e:
                    error_msg = f"Error processing customer {customer['_id']}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
            
            logger.info(f"Daily interest calculation completed. Processed: {processed_count}, Errors: {len(errors)}")
            
            if errors:
                logger.warning(f"Errors during batch job: {errors}")
            
        except Exception as e:
            logger.error(f"Critical error in daily interest calculation batch job: {str(e)}", exc_info=True)
    
    @staticmethod
    def shutdown_scheduler():
        """Gracefully shutdown the scheduler"""
        if BatchJobScheduler.scheduler and BatchJobScheduler.scheduler.running:
            BatchJobScheduler.scheduler.shutdown()
            logger.info("Batch scheduler shutdown successfully")
