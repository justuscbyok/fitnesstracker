from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import List, Optional
from datetime import timedelta

from ..models.schemas import User, UserCreate, UserUpdate, Token
from ..utils.auth import (
    authenticate_user, create_access_token, 
    get_current_active_user, ACCESS_TOKEN_EXPIRE_MINUTES
)
from ..db import crud

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "User not found"}}
)

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate):
    """
    Register a new user
    """
    # Check if username or email already exists
    db_user_by_username = crud.get_user_by_username(user.username)
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_user_by_email = crud.get_user_by_email(user.email)
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    return crud.create_user(user)

@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Get current user
    """
    return current_user

@router.put("/me", response_model=User)
def update_user_me(user_update: UserUpdate, current_user: User = Depends(get_current_active_user)):
    """
    Update current user
    """
    updated_user = crud.update_user(current_user.id, user_update)
    if updated_user is None:
        raise HTTPException(status_code=400, detail="Failed to update user")
    return updated_user

@router.get("/", response_model=List[User])
def read_users(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_active_user)):
    """
    Retrieve users - only accessible to logged in users
    """
    users = crud.get_users()
    return users[skip: skip + limit]

@router.get("/{user_id}", response_model=User)
def read_user(user_id: int, current_user: User = Depends(get_current_active_user)):
    """
    Get a specific user by ID
    """
    db_user = crud.get_user(user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user 