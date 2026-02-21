from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from bson import ObjectId

# ==================== ENUMS ====================

class RiskCategory(str, Enum):
    EXCELLENT = 'excellent'
    AVERAGE = 'average'
    HIGH_RISK = 'high_risk'
    NPA = 'npa'  # Non-Performing Asset

class TransactionType(str, Enum):
    SALE_ON_CREDIT = 'sale_on_credit'
    CASH_PAYMENT = 'cash_payment'
    INTEREST_APPLIED = 'interest_applied'
    NPA_WRITEOFF = 'npa_writeoff'
    LEGACY_BALANCE_FORWARD = 'legacy_balance_forward'
    ITEM_RETURN = 'item_return'
    PARTIAL_PAYMENT = 'partial_payment'

class EntryType(str, Enum):
    DEBIT = 'DR'
    CREDIT = 'CR'

class InterestStatus(str, Enum):
    ACCRUING = 'accruing'
    FROZEN = 'frozen'
    SETTLED = 'settled'

class PaymentBehavior(str, Enum):
    ON_TIME_PAYER = 'on_time_payer'
    FREQUENT_DELAYS = 'frequent_delays'
    HIGH_DEBT_RISK = 'high_debt_risk'
    MAINTAINS_WELL = 'maintains_well'

# ==================== CUSTOMER ACCOUNT ====================

class CustomerAccountBase(BaseModel):
    full_name: str = Field(..., description="Customer's full name")
    father_name: Optional[str] = Field(None, description="Father's name (crucial for rural areas)")
    phone_number: str = Field(..., regex=r'^[0-9]{10}$', description="10-digit phone number")
    village_ward: str = Field(..., description="Village/Ward for filtering")
    street_mohalla: Optional[str] = None
    landmark: Optional[str] = None
    pincode: Optional[str] = Field(None, regex=r'^[0-9]{6}$')
    aadhar_number: Optional[str] = Field(None, description="12-digit Aadhar (encrypted)")
    voter_id: Optional[str] = None
    
class CustomerAccountCreate(CustomerAccountBase):
    pass

class CustomerAccount(CustomerAccountBase):
    account_id: str = Field(..., description="Unique account identifier")
    risk_category: RiskCategory = RiskCategory.AVERAGE
    payment_behavior: Optional[PaymentBehavior] = None
    total_outstanding: float = 0.0
    is_active: bool = True
    manual_flags: List[str] = []  # ["good_maintainer", "do_not_credit", etc.]
    created_at: datetime
    updated_at: datetime

# ==================== LEDGER TRANSACTION ====================

class LedgerTransactionBase(BaseModel):
    transaction_type: TransactionType
    promised_return_date: Optional[datetime] = None
    notes: Optional[str] = None
    total_amount: float
    freeze_interest: bool = False  # Manual override to stop interest accrual

class LedgerTransactionCreate(LedgerTransactionBase):
    transaction_date: datetime

class LedgerTransaction(LedgerTransactionBase):
    transaction_id: str
    transaction_date: datetime
    shop_owner_id: str
    created_at: datetime
    updated_at: datetime

# ==================== LEDGER ENTRY (Double-Entry Lines) ====================

class LedgerEntryBase(BaseModel):
    entry_type: EntryType
    amount: float
    interest_status: InterestStatus = InterestStatus.ACCRUING

class LedgerEntryCreate(LedgerEntryBase):
    transaction_id: str
    account_id: str  # Links to Customer_Account or internal accounts

class LedgerEntry(LedgerEntryBase):
    entry_id: str
    transaction_id: str
    account_id: str
    created_at: datetime

# ==================== INTEREST CALCULATION ====================

class InterestCalculationRequest(BaseModel):
    account_id: str
    principal_amount: float
    months_overdue: float
    interest_rate: float = 0.02  # 2% per month

class InterestCalculationResponse(BaseModel):
    account_id: str
    principal: float
    daily_interest_rate: float
    interest_amount: float
    calculation_date: datetime

# ==================== PAYMENT ALLOCATION (Waterfall Method) ====================

class PaymentAllocationRequest(BaseModel):
    account_id: str
    payment_amount: float
    payment_date: datetime

class PaymentAllocationResponse(BaseModel):
    account_id: str
    interest_paid: float
    principal_paid: float
    remaining_balance: float
    remaining_interest: float

# ==================== BULK IMPORT ====================

class BulkImportRow(BaseModel):
    customer_name: str
    father_name: Optional[str] = None
    phone_number: str
    village_ward_street: Optional[str] = None
    aadhar_number: Optional[str] = None
    legacy_debt_amount: float
    debt_as_of_date: str  # DD/MM/YYYY
    promised_return_date: str  # DD/MM/YYYY
    notes: Optional[str] = None

class BulkImportResponse(BaseModel):
    total_rows: int
    successfully_imported: int
    failed_rows: List[dict]  # Contains row number and error message
    import_timestamp: datetime

# ==================== DASHBOARD ANALYTICS ====================

class VillageWiseReport(BaseModel):
    village_name: str
    total_outstanding: float
    number_of_accounts: int
    high_risk_accounts: int
    npa_accounts: int
    total_interest_accrued: float

class DashboardMetrics(BaseModel):
    total_money_out: float
    total_interest_accrued: float
    total_npa_written_off: float
    active_accounts: int
    high_risk_accounts: int
    npa_accounts: int
    on_time_payers: int
    frequent_defaulters: int

class FilteredOutstandingReport(BaseModel):
    date_range_start: datetime
    date_range_end: datetime
    village_filter: Optional[str] = None
    ward_filter: Optional[str] = None
    outstanding_by_customer: List[dict]  # [{customer_name, outstanding_amount, overdue_days}]
    total_outstanding_in_filter: float

# ==================== MEMO & RECEIPT ====================

class TransactionMemoRequest(BaseModel):
    transaction_id: str
    language: str = 'hi'  # 'hi' or 'en'

class TransactionMemo(BaseModel):
    customer_name: str
    previous_balance: float
    current_transaction: float
    total_outstanding: float
    promised_return_date: Optional[datetime]
    interest_disclaimer: str
    generated_at: datetime
    memo_text: str  # Formatted text for printing/SMS
