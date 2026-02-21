from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid objectid')
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type='string')

# ==================== AUTH MODELS ====================

class UserRegister(BaseModel):
    phone_number: str = Field(..., regex=r'^[0-9]{10}$')
    pin: str = Field(..., regex=r'^[0-9]{4}$')
    shop_name: str
    owner_name: str
    address: str
    
    class Config:
        schema_extra = {
            'example': {
                'phone_number': '9876543210',
                'pin': '1234',
                'shop_name': 'राज किराना',
                'owner_name': 'राज कुमार',
                'address': 'मुख्य बाजार, पुणे'
            }
        }

class UserLogin(BaseModel):
    phone_number: str = Field(..., regex=r'^[0-9]{10}$')
    pin: str = Field(..., regex=r'^[0-9]{4}$')

class User(BaseModel):
    id: Optional[PyObjectId] = Field(alias='_id')
    phone_number: str
    pin_hash: str
    shop_name: str
    owner_name: str
    address: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_schema_extra = {
            'example': {
                '_id': '507f1f77bcf86cd799439011',
                'phone_number': '9876543210',
                'shop_name': 'राज किराना',
                'owner_name': 'राज कुमार',
                'address': 'मुख्य बाजार, पुणे',
                'created_at': '2024-01-15T10:30:00',
                'updated_at': '2024-01-15T10:30:00',
                'is_active': True
            }
        }

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    user_id: str
    shop_name: str

# ==================== CUSTOMER MODELS ====================

class CustomerType(str, Enum):
    INDIVIDUAL = 'individual'
    BUSINESS = 'business'

class Customer(BaseModel):
    id: Optional[PyObjectId] = Field(alias='_id')
    user_id: str  # Shop owner ID
    name: str
    phone_number: Optional[str] = Field(None, regex=r'^[0-9]{10}$')
    address: str
    customer_type: CustomerType = CustomerType.INDIVIDUAL
    credit_limit: float = 0.0
    total_credit: float = 0.0
    total_paid: float = 0.0
    outstanding_amount: float = 0.0
    interest_rate: float = 2.0  # 2% per month
    kyc_verified: bool = False
    kyc_doc_type: Optional[str] = None
    kyc_doc_number: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

class CustomerCreate(BaseModel):
    name: str
    phone_number: Optional[str] = Field(None, regex=r'^[0-9]{10}$')
    address: str
    customer_type: CustomerType = CustomerType.INDIVIDUAL
    credit_limit: float = 0.0

# ==================== TRANSACTION MODELS ====================

class TransactionType(str, Enum):
    CREDIT = 'credit'
    PAYMENT = 'payment'
    INTEREST = 'interest'

class Transaction(BaseModel):
    id: Optional[PyObjectId] = Field(alias='_id')
    user_id: str  # Shop owner ID
    customer_id: str
    transaction_type: TransactionType
    amount: float
    description: str
    note: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

class TransactionCreate(BaseModel):
    customer_id: str
    transaction_type: TransactionType
    amount: float
    description: str
    note: Optional[str] = None

# ==================== INTEREST MODELS ====================

class InterestCalculation(BaseModel):
    id: Optional[PyObjectId] = Field(alias='_id')
    user_id: str
    customer_id: str
    principal: float
    interest_rate: float
    interest_amount: float
    calculation_date: datetime
    created_at: datetime
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

class PaymentSchedule(BaseModel):
    id: Optional[PyObjectId] = Field(alias='_id')
    user_id: str
    customer_id: str
    due_amount: float
    due_date: datetime
    paid_amount: float = 0.0
    payment_status: str = 'pending'  # pending, partial, completed
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
