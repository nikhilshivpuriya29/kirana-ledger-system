from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from models import Account, LedgerEntry, InterestEntry, RiskFlag
from typing import List, Dict

class RiskManagementEngine:
    """
    Behavioral flagging and risk assessment engine for accounts.
    
    Automated Flags:
    - On-Time Payer: Consistent on-time payments
    - Frequent Delays: Multiple delayed payments
    - High Debt Risk: Outstanding balance exceeds threshold
    
    Manual Flags:
    - Good in maintaining account
    - Do not give further credit
    - NPA (Non-Performing Asset)
    """
    
    # Configuration
    HIGH_DEBT_THRESHOLD = 50000  # Rupees
    DELAY_THRESHOLD_DAYS = 15  # Days after promised date
    FREQUENT_DELAY_COUNT = 3  # Number of delays to flag as frequent
    ON_TIME_PAYMENT_COUNT = 5  # Consecutive on-time payments
    
    @staticmethod
    def evaluate_account_risk(account_id: str, db: Session) -> Dict:
        """
        Comprehensive account risk evaluation.
        """
        account = db.query(Account).filter(Account.account_id == account_id).first()
        if not account:
            return {"status": "error", "message": "Account not found"}
        
        # Get all ledger entries for this account
        ledger_entries = db.query(LedgerEntry).filter(
            LedgerEntry.account_id == account_id
        ).order_by(LedgerEntry.promised_date.desc()).all()
        
        # Get current risk flags
        current_flags = db.query(RiskFlag).filter(
            RiskFlag.account_id == account_id,
            RiskFlag.status == "active"
        ).all()
        
        flags_to_add = []
        flags_to_remove = []
        
        # Risk evaluation logic
        
        # 1. Check for High Debt Risk
        if account.outstanding_balance > RiskManagementEngine.HIGH_DEBT_THRESHOLD:
            if not any(f.flag_type == "high_debt_risk" for f in current_flags):
                flags_to_add.append("high_debt_risk")
        else:
            # Remove high debt flag if balance is below threshold
            for flag in current_flags:
                if flag.flag_type == "high_debt_risk":
                    flags_to_remove.append(flag)
        
        # 2. Analyze payment behavior
        delayed_count = 0
        on_time_count = 0
        total_transactions = 0
        
        for entry in ledger_entries[:20]:  # Check last 20 transactions
            if entry.entry_type == "debit":  # Credit given
                total_transactions += 1
                if entry.promised_date:
                    # If entry is paid
                    if entry.status == "completed":
                        # Check if paid on time
                        if entry.paid_date and entry.paid_date <= entry.promised_date:
                            on_time_count += 1
                        else:
                            delayed_count += 1
                    else:
                        # Check if currently overdue
                        if datetime.now() > entry.promised_date + timedelta(days=RiskManagementEngine.DELAY_THRESHOLD_DAYS):
                            delayed_count += 1
        
        # Apply behavioral flags
        if delayed_count >= RiskManagementEngine.FREQUENT_DELAY_COUNT:
            if not any(f.flag_type == "frequent_delays" for f in current_flags):
                flags_to_add.append("frequent_delays")
        else:
            for flag in current_flags:
                if flag.flag_type == "frequent_delays":
                    flags_to_remove.append(flag)
        
        if on_time_count >= RiskManagementEngine.ON_TIME_PAYMENT_COUNT and delayed_count == 0:
            if not any(f.flag_type == "on_time_payer" for f in current_flags):
                flags_to_add.append("on_time_payer")
        else:
            for flag in current_flags:
                if flag.flag_type == "on_time_payer":
                    flags_to_remove.append(flag)
        
        # 3. Check for NPA (overdue beyond 90 days)
        overdue_entries = db.query(LedgerEntry).filter(
            LedgerEntry.account_id == account_id,
            LedgerEntry.status == "pending",
            LedgerEntry.promised_date < datetime.now() - timedelta(days=90)
        ).all()
        
        if len(overdue_entries) > 0:
            if not any(f.flag_type == "npa" for f in current_flags):
                flags_to_add.append("npa")
                # Set account status
                account.account_status = "npa"
        
        # Add new flags to database
        for flag_type in flags_to_add:
            new_flag = RiskFlag(
                flag_id=f"FLAG-{datetime.now().timestamp()}",
                account_id=account_id,
                flag_type=flag_type,
                flag_date=datetime.now(),
                status="active",
                description=RiskManagementEngine._get_flag_description(flag_type)
            )
            db.add(new_flag)
        
        # Remove inactive flags
        for flag in flags_to_remove:
            flag.status = "inactive"
            flag.updated_date = datetime.now()
        
        db.commit()
        
        return {
            "account_id": account_id,
            "account_status": account.account_status,
            "outstanding_balance": account.outstanding_balance,
            "delayed_payments": delayed_count,
            "on_time_payments": on_time_count,
            "total_transactions": total_transactions,
            "flags_added": flags_to_add,
            "flags_removed": [f.flag_type for f in flags_to_remove],
            "current_flags": [(f.flag_type, f.description) for f in current_flags + [RiskFlag(flag_type=ft, description=RiskManagementEngine._get_flag_description(ft)) for ft in flags_to_add]],
            "risk_level": RiskManagementEngine._calculate_risk_level(flags_to_add, delayed_count, on_time_count)
        }
    
    @staticmethod
    def apply_manual_flag(account_id: str, flag_type: str, reason: str, db: Session) -> Dict:
        """
        Apply manual flags (operator decision):
        - good_account_maintenance
        - no_further_credit
        - npa (programmatic, but can be manual override)
        """
        account = db.query(Account).filter(Account.account_id == account_id).first()
        if not account:
            return {"status": "error", "message": "Account not found"}
        
        # Create manual flag
        flag = RiskFlag(
            flag_id=f"FLAG-{datetime.now().timestamp()}",
            account_id=account_id,
            flag_type=flag_type,
            flag_date=datetime.now(),
            status="active",
            description=reason,
            is_manual=True
        )
        
        db.add(flag)
        
        # Update account status if NPA
        if flag_type == "npa":
            account.account_status = "npa"
        elif flag_type == "no_further_credit":
            account.account_status = "blocked"
        
        db.commit()
        
        return {
            "status": "success",
            "message": f"Flag {flag_type} applied to account",
            "flag_id": flag.flag_id,
            "account_status": account.account_status
        }
    
    @staticmethod
    def _get_flag_description(flag_type: str) -> str:
        descriptions = {
            "on_time_payer": "Consistent on-time payment history",
            "frequent_delays": "Multiple delayed payments detected",
            "high_debt_risk": "Outstanding balance exceeds safe threshold",
            "npa": "Non-Performing Asset - overdue beyond 90 days",
            "good_account_maintenance": "Maintains account well, reliable customer",
            "no_further_credit": "Do not extend further credit to this customer",
        }
        return descriptions.get(flag_type, f"Flag: {flag_type}")
    
    @staticmethod
    def _calculate_risk_level(flags: List[str], delayed: int, on_time: int) -> str:
        """
        Calculate overall risk level.
        """
        risk_score = 0
        
        if "npa" in flags:
            return "critical"
        if "no_further_credit" in flags:
            return "critical"
        if "high_debt_risk" in flags:
            risk_score += 3
        if "frequent_delays" in flags:
            risk_score += 2
        if "on_time_payer" in flags:
            risk_score -= 1
        
        if delayed > on_time:
            risk_score += 1
        
        if risk_score >= 4:
            return "high"
        elif risk_score >= 2:
            return "medium"
        else:
            return "low"
    
    @staticmethod
    def get_account_risk_profile(account_id: str, db: Session) -> Dict:
        """
        Get complete risk profile for account.
        """
        account = db.query(Account).filter(Account.account_id == account_id).first()
        if not account:
            return {"status": "error", "message": "Account not found"}
        
        flags = db.query(RiskFlag).filter(
            RiskFlag.account_id == account_id,
            RiskFlag.status == "active"
        ).all()
        
        return {
            "account_id": account_id,
            "account_status": account.account_status,
            "customer_name": account.customer_name if hasattr(account, 'customer_name') else "Unknown",
            "outstanding_balance": account.outstanding_balance,
            "total_paid": account.total_paid,
            "active_flags": [
                {
                    "flag_type": f.flag_type,
                    "description": f.description,
                    "flag_date": f.flag_date.isoformat() if f.flag_date else None,
                    "is_manual": f.is_manual if hasattr(f, 'is_manual') else False
                }
                for f in flags
            ],
            "credit_recommendation": "DENIED" if any(f.flag_type in ["npa", "no_further_credit"] for f in flags) else "ALLOWED"
        }
