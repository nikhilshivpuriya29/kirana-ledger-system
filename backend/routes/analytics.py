from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List
from database import get_db
from models import Account, Customer, LedgerTransaction, LedgerEntry, InterestEntry
from sqlalchemy import func, and_

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/dashboard/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    Global dashboard summary:
    - Total money out (total outstanding balance)
    - Total collections
    - Number of customers
    - Active accounts
    - Pending interest charges
    """
    try:
        # Total outstanding balance
        total_outstanding = db.query(func.sum(Account.outstanding_balance)).scalar() or 0
        
        # Total collections (paid)
        total_paid = db.query(func.sum(Account.total_paid)).scalar() or 0
        
        # Total accounts
        total_accounts = db.query(func.count(Account.account_id)).scalar() or 0
        
        # Active accounts (status = "active")
        active_accounts = db.query(func.count(Account.account_id)).filter(
            Account.account_status == "active"
        ).scalar() or 0
        
        # NPA accounts
        npa_accounts = db.query(func.count(Account.account_id)).filter(
            Account.account_status == "npa"
        ).scalar() or 0
        
        # Pending interest
        pending_interest = db.query(func.sum(InterestEntry.amount)).filter(
            InterestEntry.status == "pending",
            InterestEntry.interest_type == "interest"
        ).scalar() or 0
        
        # Pending penalties
        pending_penalties = db.query(func.sum(InterestEntry.amount)).filter(
            InterestEntry.status == "pending",
            InterestEntry.interest_type == "penalty"
        ).scalar() or 0
        
        # Overdue (more than 15 days past promised date)
        overdue_threshold = datetime.now() - timedelta(days=15)
        overdue_entries = db.query(func.sum(LedgerEntry.amount)).filter(
            LedgerEntry.status == "pending",
            LedgerEntry.promised_date < overdue_threshold
        ).scalar() or 0
        
        return {
            "status": "success",
            "macro_view": {
                "total_money_out": total_outstanding,
                "total_collections": total_paid,
                "total_accounts": total_accounts,
                "active_accounts": active_accounts,
                "npa_accounts": npa_accounts,
                "pending_interest_charges": pending_interest,
                "pending_penalties": pending_penalties,
                "overdue_amount": overdue_entries
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/dashboard/village/{village_name}")
def get_village_dashboard(village_name: str, db: Session = Depends(get_db)):
    """
    Village-wise filtered dashboard view.
    
    Metrics:
    - Total outstanding in village
    - Collections
    - Number of customers
    - At-risk accounts
    - NPA accounts
    """
    try:
        # Get all customers from this village
        customers = db.query(Customer).filter(
            func.lower(Customer.village) == func.lower(village_name)
        ).all()
        
        if not customers:
            return {
                "status": "success",
                "village": village_name,
                "data": {
                    "total_outstanding": 0,
                    "total_collections": 0,
                    "total_customers": 0,
                    "active_accounts": 0,
                    "npa_accounts": 0,
                    "at_risk_accounts": 0
                }
            }
        
        customer_ids = [c.customer_id for c in customers]
        
        # Get accounts for these customers
        accounts = db.query(Account).filter(
            Account.customer_id.in_(customer_ids)
        ).all()
        
        # Calculate metrics
        total_outstanding = sum(a.outstanding_balance or 0 for a in accounts)
        total_paid = sum(a.total_paid or 0 for a in accounts)
        active_count = len([a for a in accounts if a.account_status == "active"])
        npa_count = len([a for a in accounts if a.account_status == "npa"])
        at_risk_count = len([a for a in accounts if a.account_status in ["blocked", "warning"]])
        
        return {
            "status": "success",
            "village": village_name,
            "data": {
                "total_customers": len(customers),
                "total_accounts": len(accounts),
                "total_outstanding": total_outstanding,
                "total_collections": total_paid,
                "active_accounts": active_count,
                "npa_accounts": npa_count,
                "at_risk_accounts": at_risk_count,
                "average_outstanding_per_account": total_outstanding / len(accounts) if accounts else 0
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/villages/list")
def get_villages_list(db: Session = Depends(get_db)):
    """
    Get list of all villages in the system.
    """
    try:
        villages = db.query(func.distinct(Customer.village)).filter(
            Customer.village.isnot(None)
        ).all()
        
        village_names = [v[0] for v in villages if v[0]]
        return {
            "status": "success",
            "villages": village_names,
            "total_villages": len(village_names)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/reports/transaction-summary")
def get_transaction_summary(days: int = 30, db: Session = Depends(get_db)):
    """
    Transaction summary for the last N days.
    """
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        transactions = db.query(LedgerTransaction).filter(
            LedgerTransaction.transaction_date >= start_date
        ).all()
        
        # Count by status
        pending = len([t for t in transactions if t.status == "pending"])
        completed = len([t for t in transactions if t.status == "completed"])
        
        # Total amount
        total_amount = sum(t.amount or 0 for t in transactions)
        
        return {
            "status": "success",
            "period_days": days,
            "start_date": start_date.isoformat(),
            "end_date": datetime.now().isoformat(),
            "total_transactions": len(transactions),
            "pending_transactions": pending,
            "completed_transactions": completed,
            "total_amount": total_amount
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/reports/overdue-analysis")
def get_overdue_analysis(days: int = 15, db: Session = Depends(get_db)):
    """
    Analyze overdue payments.
    
    Overdue = promised_date + days_threshold < now
    """
    try:
        threshold_date = datetime.now() - timedelta(days=days)
        
        overdue_entries = db.query(LedgerEntry).filter(
            LedgerEntry.status == "pending",
            LedgerEntry.promised_date < threshold_date
        ).all()
        
        overdue_accounts = set(e.account_id for e in overdue_entries)
        
        # Get account details
        account_details = db.query(Account).filter(
            Account.account_id.in_(list(overdue_accounts))
        ).all()
        
        total_overdue = sum(e.amount or 0 for e in overdue_entries)
        
        return {
            "status": "success",
            "overdue_threshold_days": days,
            "total_overdue_entries": len(overdue_entries),
            "total_accounts_with_overdue": len(overdue_accounts),
            "total_overdue_amount": total_overdue,
            "average_overdue_per_account": total_overdue / len(account_details) if account_details else 0,
            "overdue_accounts": [
                {
                    "account_id": a.account_id,
                    "outstanding_balance": a.outstanding_balance,
                    "status": a.account_status
                }
                for a in account_details[:10]  # Top 10 overdue accounts
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/reports/payment-behavior")
def get_payment_behavior_report(db: Session = Depends(get_db)):
    """
    Analyze overall payment behavior patterns.
    """
    try:
        # Get all accounts
        accounts = db.query(Account).all()
        
        on_time_payers = 0
        frequent_delayers = 0
        high_risk = 0
        
        for account in accounts:
            # Get entries for this account
            entries = db.query(LedgerEntry).filter(
                LedgerEntry.account_id == account.account_id,
                LedgerEntry.entry_type == "debit"
            ).all()
            
            if entries:
                completed = [e for e in entries if e.status == "completed"]
                if completed:
                    on_time = len([e for e in completed if e.paid_date and e.paid_date <= e.promised_date])
                    delayed = len(completed) - on_time
                    
                    if delayed == 0 and on_time >= 3:
                        on_time_payers += 1
                    elif delayed >= 2:
                        frequent_delayers += 1
                    
                    if account.outstanding_balance > 50000:
                        high_risk += 1
        
        return {
            "status": "success",
            "total_accounts": len(accounts),
            "on_time_payers": on_time_payers,
            "frequent_delayers": frequent_delayers,
            "high_risk_accounts": high_risk,
            "on_time_percentage": (on_time_payers / len(accounts) * 100) if accounts else 0,
            "risk_percentage": (high_risk / len(accounts) * 100) if accounts else 0
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
