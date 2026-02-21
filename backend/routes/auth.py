from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timedelta
import os
from passlib.context import CryptContext
from jose import JWTError, jwt
from models import UserRegister, UserLogin, User, TokenResponse
from database import db, COLLECTIONS

router = APIRouter(prefix="/api/auth", tags=["authentication"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        os.getenv("JWT_SECRET_KEY", "your-secret-key"),
        algorithm=os.getenv("JWT_ALGORITHM", "HS256")
    )
    return encoded_jwt

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister):
    """Register a new shop owner"""
    db_connection = db.get_database()
    
    # Check if user already exists
    existing_user = db_connection[COLLECTIONS['users']].find_one(
        {"phone_number": user_data.phone_number}
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )
    
    # Create new user
    user_dict = user_data.dict()
    user_dict["pin_hash"] = hash_password(user_data.pin)
    del user_dict["pin"]
    user_dict["created_at"] = datetime.utcnow()
    user_dict["updated_at"] = datetime.utcnow()
    user_dict["is_active"] = True
    
    result = db_connection[COLLECTIONS['users']].insert_one(user_dict)
    user_id = str(result.inserted_id)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user_id, "phone_number": user_data.phone_number}
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user_id,
        shop_name=user_data.shop_name
    )

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Login with phone number and PIN"""
    db_connection = db.get_database()
    
    # Find user
    user = db_connection[COLLECTIONS['users']].find_one(
        {"phone_number": credentials.phone_number}
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone number or PIN"
        )
    
    # Verify PIN
    if not verify_password(credentials.pin, user["pin_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone number or PIN"
        )
    
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    user_id = str(user["_id"])
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user_id, "phone_number": credentials.phone_number}
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user_id,
        shop_name=user["shop_name"]
    )

@router.get("/me", response_model=User)
async def get_current_user(token: str):
    """Get current logged-in user details"""
    try:
        payload = jwt.decode(
            token,
            os.getenv("JWT_SECRET_KEY", "your-secret-key"),
            algorithms=[os.getenv("JWT_ALGORITHM", "HS256")]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    db_connection = db.get_database()
    from bson import ObjectId
    user = db_connection[COLLECTIONS['users']].find_one(
        {"_id": ObjectId(user_id)}
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return User(**user)
