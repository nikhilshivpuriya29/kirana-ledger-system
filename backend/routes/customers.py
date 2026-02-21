from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from bson import ObjectId
from models import Customer, CustomerCreate
from database import db, COLLECTIONS

router = APIRouter(prefix="/api/customers", tags=["customers"])

@router.post("/", response_model=Customer)
async def create_customer(customer_data: CustomerCreate, user_id: str):
    """Create a new customer"""
    db_connection = db.get_database()
    
    customer_dict = customer_data.dict()
    customer_dict["user_id"] = user_id
    customer_dict["created_at"] = datetime.utcnow()
    customer_dict["updated_at"] = datetime.utcnow()
    customer_dict["is_active"] = True
    customer_dict["total_credit"] = 0.0
    customer_dict["total_paid"] = 0.0
    customer_dict["outstanding_amount"] = 0.0
    
    result = db_connection[COLLECTIONS['customers']].insert_one(customer_dict)
    customer_dict["_id"] = result.inserted_id
    
    return Customer(**customer_dict)

@router.get("/{customer_id}", response_model=Customer)
async def get_customer(customer_id: str, user_id: str):
    """Get customer details"""
    db_connection = db.get_database()
    
    customer = db_connection[COLLECTIONS['customers']].find_one({
        "_id": ObjectId(customer_id),
        "user_id": user_id
    })
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    return Customer(**customer)

@router.get("/", response_model=list)
async def list_customers(user_id: str, skip: int = 0, limit: int = 100):
    """List all customers for a shop owner"""
    db_connection = db.get_database()
    
    customers = db_connection[COLLECTIONS['customers']].find(
        {"user_id": user_id, "is_active": True}
    ).skip(skip).limit(limit)
    
    return [Customer(**customer) for customer in customers]

@router.put("/{customer_id}", response_model=Customer)
async def update_customer(customer_id: str, customer_data: CustomerCreate, user_id: str):
    """Update customer information"""
    db_connection = db.get_database()
    
    update_data = customer_data.dict()
    update_data["updated_at"] = datetime.utcnow()
    
    result = db_connection[COLLECTIONS['customers']].find_one_and_update(
        {"_id": ObjectId(customer_id), "user_id": user_id},
        {"$set": update_data},
        return_document=True
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    return Customer(**result)
