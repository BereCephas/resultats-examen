from fastapi import APIRouter, Form, HTTPException, status
from fastapi.security import HTTPBearer
from api.auth.models import UserModel
from api.auth.schemas import Token, UserLogin
from api.core.security import create_access_token
from datetime import timedelta

auth_router = APIRouter()
security = HTTPBearer()

@auth_router.post("/login", response_model=Token)
async def login(
    username: str = Form(...),
    password: str = Form(...)
):
    """Admin login endpoint"""
    user = UserModel.authenticate_user(username, password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if user['role'] not in ['admin', 'operator']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access admin panel"
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user['username']}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }