from fastapi import APIRouter ,Depends,HTTPException,status,Body
from sqlalchemy.orm import Session
from app import models, schemas
from core.database import get_db
from sqlalchemy import func
from uuid import UUID
from core.email import  send_reset_email
import random
import datetime
from core.security import get_password_hash,verify_password,create_access_token
from core.auth import get_current_active_user 
import re


router = APIRouter(
    prefix="/users",
    tags=["User Management"],
)


# Create a new user (no authentication required)
@router.post("/",response_model=schemas.User, status_code=status.HTTP_201_CREATED,
              summary="Create a new user")
def create_user(user: schemas.UserCreate, db:Session = Depends(get_db)):
    # Check if username is already registered
    db_user=(db.query(models.User).filter(models.User.username==user.username).first())
    if db_user:
        raise HTTPException(status_code=400, detail="Username is already registered")
    
    # Check if email is already registered
    db_user = db.query(models.User).filter(models.User.email==user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Password validation rules
    min_length = 8
    has_uppercase = re.search(r"[A-Z]", user.password)
    has_lowercase = re.search(r"[a-z]", user.password)
    has_digit = re.search(r"[0-9]", user.password)
    has_special = re.search(r"[^a-zA-Z0-9\s]", user.password)

    errors = []
    if len(user.password) < min_length:
        errors.append(f"Password must be at least {min_length} characters long")
    if not has_uppercase:
        errors.append("Password must contain at least one uppercase letter")
    if not has_lowercase:
        errors.append("Password must contain at least one lowercase letter")
    if not has_digit:
        errors.append("Password must contain at least one digit")
    if not has_special:
        errors.append("Password must contain at least one special character")

    if errors:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=errors)
    
    # Hashed the password before storing it 
    hashed_password = get_password_hash(user.password)

    # Add the user to the database session
    db_user = models.User(username=user.username,email=user.email,hashed_password=hashed_password,role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user



# Get All users (requires authentication)
@router.get('/',response_model=schemas.UserListResponse, summary="Get all users", dependencies=[Depends(get_current_active_user)])
def read_users(page: int = 0, limit: int = 100, db: Session = Depends(get_db), username: str = None):
    print(f"Database session in read_users: {db}")
    query = db.query(models.User)

    if username:
        query = query.filter(func.lower(models.User.username).like(f"%{username.lower()}%"))
    
    total= query.count()
    users= query.offset(page * limit).limit(limit).all()

    return {"data": users, "limit": limit, "page": page, "total": total}



# Get user by ID (requires authentication)
@router.get("/{user_id}",response_model=schemas.User, summary="Get a user by ID", dependencies=[Depends(get_current_active_user)])
def read_user(user_id:UUID, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id==user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404,detail="User not found")
    return db_user


# Update User (requires authentication)
@router.put("/{user_id}",response_model=schemas.User,summary="Update a user", dependencies=[Depends(get_current_active_user)])
def update_user(
    user_id:UUID,
    user:schemas.UserUpdate = Body(...,description="The updated user data"),
    db:Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(models.User.id==user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404,detail="User not found")
    for key , value in user.dict().items():
     setattr(db_user,key,value)
    db.commit()
    db.refresh(db_user)
    return db_user


# Delete Users (requires authentication)
@router.delete("/{user_id}",response_model=schemas.DeleteResponse, dependencies=[Depends(get_current_active_user)])
def delete_user(user_id:UUID,db:Session=Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id==user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404,detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"detail":"User deleted Successfully"}


# Login for access token
@router.post("/token", response_model=schemas.Token, summary="Get access token")
def login_for_access_token(
    request_body:schemas.TokenRequest,
    db:Session = Depends(get_db)
):
   user = db.query(models.User).filter(models.User.username == request_body.username).first()
   if not user or not verify_password(request_body.password,user.hashed_password) :
       raise HTTPException(
           status_code=status.HTTP_401_UNAUTHORIZED,
           detail="Incorrect username or password",
           headers={"www-Authenticate": "Bearer"}
       )
   access_token = create_access_token(data={"sub": str(user.id)})
   return {"access_token": access_token, "token_type": "bearer"}


# Reset Password 
@router.post("/reset-password", status_code=status.HTTP_200_OK, summary="Request password reset")
def request_password_reset(
    reset_request: schemas.PasswordResetRequest, db: Session= Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == reset_request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    #Generate OTP
    otp = str(random.randint(100000, 999999))
    expire_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=10) 

    #Store OTP and expiration
    user.reset_token = otp
    user.reset_token_expires_at = expire_at
    db.commit()

    #Send email
    send_reset_email(reset_request.email, otp)

    return {"detail": "Password reset email sent"}
    
 

# Verify the Passwords
@router.post("/reset-password/verify", status_code=status.HTTP_200_OK, summary="Verify OTP and reset password")
def verify_password_reset(
    verification: schemas.PasswordResetVerify, db: Session = Depends(get_db) 
 ):
     user = db.query(models.User).filter(models.User.email == verification.email).first()
     if not user:
         raise HTTPException(status_code=404, detail="User not found")
     
     if user.reset_token != verification.otp:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")
    
     if datetime.datetime.utcnow() > user.reset_token_expires_at:
        raise HTTPException(status_code=400, detail="OTP expired")

    # Update password
     hashed_password = get_password_hash(verification.new_password)
     user.hashed_password = hashed_password
     user.reset_token = None
     user.reset_token_expires_at = None
     db.commit()
    
     return {"detail": "Password reset successful"}
     