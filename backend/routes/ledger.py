from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
from database import get_db
from models import (
    Customer, Account, LedgerTransaction, LedgerEntry,
    InterestEntry, RiskFlag
)
from services.interest_engine import InterestCalculationEngine
from pydantic import BaseModel

router = APIRouter(prefix="/ledger", tags=["ledger"])

# Pydantic models for requests
class LedgerEntryCreate(BaseModel):
    account_id: str
    entry_type: str  # "debit" or "credit"
    description: str
    amount: float
    promised_date: datetime
    items_description: Optional[str] = None

class TransactionResponse(BaseModel):
    transaction_id: str
    account_id: str
    transaction_date: datetime
    debit_entries: list
    credit_entries: list
    status: str

@router.post("/transaction", response_model=dict)
def create_transaction(transaction: LedgerEntryCreate, db: Session = Depends(get_db)):
    """
    Create a double-entry ledger transaction.
    
    - Record what was taken (Items/Cash)
    - Exact Date and Time
    - Principal Amount
    - Promised Return Date
    """
    try:
        # Get account
        account = db.query(Account).filter(Account.account_id == transaction.account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Get customer for validation
        customer = db.query(Customer).filter(Customer.customer_id == account.customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Create transaction record
        txn = LedgerTransaction(
            transaction_id=f"TXN-{datetime.now().timestamp()}",
            account_id=transaction.account_id,
            transaction_date=datetime.now(),
            transaction_type="credit" if transaction.entry_type == "debit" else "debit",
            description=transaction.description,
            status="pending"
        )
        db.add(txn)
        db.flush()
        
        # Create debit entry (what customer owes - increase liability)
        debit_entry = LedgerEntry(
            entry_id=f"ENTRY-{datetime.now().timestamp()}-DR",
            transaction_id=txn.transaction_id,
            account_id=transaction.account_id,
            entry_type="debit",
            amount=transaction.amount,
            description=transaction.description,
            items_description=transaction.items_description,
            entry_date=datetime.now(),
            promised_date=transaction.promised_date
        )
        
        # Create credit entry (cash/inventory out - decrease assets)
        credit_entry = LedgerEntry(
            entry_id=f"ENTRY-{datetime.now().timestamp()}-CR",
            transaction_id=txn.transaction_id,
            account_id=transaction.account_id,
            entry_type="credit",
            amount=transaction.amount,
            description=f"Outflow for {transaction.description}",
            entry_date=datetime.now(),
            promised_date=transaction.promised_date
        )
        
        db.add_all([debit_entry, credit_entry])
        
        # Update account balance (outstanding amount)
        account.outstanding_balance = (account.outstanding_balance or 0) + transaction.amount
        account.last_transaction_date = datetime.now()
        
        db.commit()
        
        return {
            "status": "success",
            "transaction_id": txn.transaction_id,
            "account_id": account.account_id,
            "amount": transaction.amount,
            "transaction_date": datetime.now().isoformat(),
            "message": "Transaction recorded successfully"
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/payment")
def process_payment(account_id: str, amount: float, payment_date: Optional[datetime] = None, db: Session = Depends(get_db)):
    """
    Process payment with waterfall allocation:
    1. Oldest pending interest
    2. Oldest pending penalties
    3. Oldest principal
    """
    try:
        payment_date = payment_date or datetime.now()
        account = db.query(Account).filter(Account.account_id == account_id).first()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        remaining_amount = amount
        allocations = []
        
        # Step 1: Allocate to pending interest (oldest first)
        pending_interest = db.query(InterestEntry).filter(
            InterestEntry.account_id == account_id,
            InterestEntry.status == "pending",
            InterestEntry.interest_type == "interest"
        ).order_by(InterestEntry.interest_date).all()
        
        for interest in pending_interest:
            if remaining_amount <= 0:
                break
            allocated = min(remaining_amount, interest.amount - (interest.paid_amount or 0))
            interest.paid_amount = (interest.paid_amount or 0) + allocated
            if interest.paid_amount >= interest.amount:
                interest.status = "completed"
            allocations.append({"type": "interest", "amount": allocated, "entry_id": interest.entry_id})
            remaining_amount -= allocated
        
        # Step 2: Allocate to penalties
        pending_penalties = db.query(InterestEntry).filter(
            InterestEntry.account_id == account_id,
            InterestEntry.status == "pending",
            InterestEntry.interest_type == "penalty"
        ).order_by(InterestEntry.interest_date).all()
        
        for penalty in pending_penalties:
            if remaining_amount <= 0:
                break
            allocated = min(remaining_amount, penalty.amount - (penalty.paid_amount or 0))
            penalty.paid_amount = (penalty.paid_amount or 0) + allocated
            if penalty.paid_amount >= penalty.amount:
                penalty.status = "completed"
            allocations.append({"type": "penalty", "amount": allocated, "entry_id": penalty.entry_id})
            remaining_amount -= allocated
        
        # Step 3: Allocate to principal
        pending_entries = db.query(LedgerEntry).filter(
            LedgerEntry.account_id == account_id,
            LedgerEntry.entry_type == "debit",
            LedgerEntry.status == "pending"
        ).order_by(LedgerEntry.promised_date).all()
        
        for entry in pending_entries:
            if remaining_amount <= 0:
                break
            allocated = min(remaining_amount, entry.amount - (entry.paid_amount or 0))
            entry.paid_amount = (entry.paid_amount or 0) + allocated
            if entry.paid_amount >= entry.amount:
                entry.status = "completed"
            allocations.append({"type": "principal", "amount": allocated, "entry_id": entry.entry_id})
            remaining_amount -= allocated
        
        # Update account
        account.outstanding_balance = max(0, account.outstanding_balance - amount)
        account.total_paid = (account.total_paid or 0) + amount
        account.last_payment_date = payment_date
        
        db.commit()
        
        return {
            "status": "success",
            "account_id": account_id,
            "payment_amount": amount,
            "allocations": allocations,
            "remaining_balance": account.outstanding_balance,
            "payment_date": payment_date.isoformat()
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/account/{account_id}/statement")
def get_account_statement(account_id: str, db: Session = Depends(get_db)):
    """
    Get complete account statement with all transactions and entries.
    """
    account = db.query(Account).filter(Account.account_id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    transactions = db.query(LedgerTransaction).filter(
        LedgerTransaction.account_id == account_id
    ).order_by(LedgerTransaction.transaction_date.desc()).all()
    
    entries = db.query(LedgerEntry).filter(
        LedgerEntry.account_id == account_id
    ).order_by(LedgerEntry.entry_date.desc()).all()
    
    interest_entries = db.query(InterestEntry).filter(
        InterestEntry.account_id == account_id
    ).order_by(InterestEntry.interest_date.desc()).all()
    
    return {
        "account_id": account_id,
        "account_status": account.account_status,
        "outstanding_balance": account.outstanding_balance,
        "total_paid": account.total_paid,
        "total_outstanding": account.outstanding_balance,
        "transactions_count": len(transactions),
        "transactions": [{"id": t.transaction_id, "date": t.transaction_date, "type": t.transaction_type, "status": t.status} for t in transactions[:10]],
        "recent_entries": [{"id": e.entry_id, "type": e.entry_type, "amount": e.amount, "date": e.entry_date} for e in entries[:10]],
        "interest_charges": [{"id": ie.entry_id, "amount": ie.amount, "type": ie.interest_type, "status": ie.status} for ie in interest_entries[:10]]
    }

@router.post("/return")
def process_return(account_id: str, entry_id: str, amount: float, reason: str, db: Session = Depends(get_db)):
    """
    Handle returns and refunds in kind.
    """
    try:
        account = db.query(Account).filter(Account.account_id == account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        entry = db.query(LedgerEntry).filter(LedgerEntry.entry_id == entry_id).first()
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found")
        
        # Create return entry (credit to offset the debit)
        return_entry = LedgerEntry(
            entry_id=f"RETURN-{datetime.now().timestamp()}",
            transaction_id=entry.transaction_id,
            account_id=account_id,
            entry_type="credit",
            amount=amount,
            description=f"Return: {reason}",
            entry_date=datetime.now(),
            status="completed"
        )
        
        db.add(return_entry)
        
        # Reduce outstanding balance
        account.outstanding_balance = max(0, account.outstanding_balance - amount)
        
        db.commit()
        
        return {
            "status": "success",
            "account_id": account_id,
            "return_entry_id": return_entry.entry_id,
            "return_amount": amount,
            "reason": reason,
            "new_balance": account.outstanding_balance
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
