"""
Authentication API endpoints for user management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta, timezone

from app.core.security import (
    authenticate_user,
    create_access_token,
    get_current_user,
    require_auth,
    get_password_hash,
)
from app.database.config import get_primary_db_session
from app.models.simple_user import SimpleUser, UserRole


router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


class LoginRequest(BaseModel):
    user_id: str
    password: str = ""  # Optional for development


class RegisterRequest(BaseModel):
    user_id: str
    username: str
    email: Optional[str] = None
    password: Optional[str] = None
    role: str = "child"
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserProfile(BaseModel):
    id: int
    user_id: str
    username: str
    email: Optional[str]
    role: str
    first_name: Optional[str]
    last_name: Optional[str]
    ui_language: str
    is_active: bool
    created_at: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserProfile


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_primary_db_session)):
    """Login user and return JWT token"""
    user = authenticate_user(db, request.user_id, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    # Update last login
    user.last_login = datetime.now(timezone.utc)
    db.commit()

    # Create access token
    access_token = create_access_token(
        data={"sub": user.user_id}, expires_delta=timedelta(minutes=30)
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserProfile(
            id=user.id,
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            role=user.role.value if user.role else "child",
            first_name=user.first_name,
            last_name=user.last_name,
            ui_language=user.ui_language,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
        ),
    )


@router.post("/register", response_model=LoginResponse)
async def register(
    request: RegisterRequest, db: Session = Depends(get_primary_db_session)
):
    """Register new user"""
    # Check if user already exists
    existing_user = (
        db.query(SimpleUser).filter(SimpleUser.user_id == request.user_id).first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User ID already exists"
        )

    # Create new user
    password_hash = None
    if request.password:
        password_hash = get_password_hash(request.password)

    try:
        role = UserRole(request.role)
    except ValueError:
        role = UserRole.CHILD

    user = SimpleUser(
        user_id=request.user_id,
        username=request.username,
        email=request.email,
        password_hash=password_hash,
        role=role,
        first_name=request.first_name,
        last_name=request.last_name,
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Create access token
    access_token = create_access_token(
        data={"sub": user.user_id}, expires_delta=timedelta(minutes=30)
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserProfile(
            id=user.id,
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            role=user.role.value,
            first_name=user.first_name,
            last_name=user.last_name,
            ui_language=user.ui_language,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
        ),
    )


@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: SimpleUser = Depends(require_auth)):
    """Get current user profile"""
    return UserProfile(
        id=current_user.id,
        user_id=current_user.user_id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role.value if current_user.role else "child",
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        ui_language=current_user.ui_language,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat(),
    )


@router.put("/profile")
async def update_profile(
    username: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    first_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    ui_language: Optional[str] = Form(None),
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """Update user profile"""
    if username:
        current_user.username = username
    if email:
        current_user.email = email
    if first_name:
        current_user.first_name = first_name
    if last_name:
        current_user.last_name = last_name
    if ui_language:
        current_user.ui_language = ui_language

    current_user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(current_user)

    return {"message": "Profile updated successfully"}


@router.get("/users", response_model=List[UserProfile])
async def list_users(
    current_user: SimpleUser = Depends(require_auth),
    db: Session = Depends(get_primary_db_session),
):
    """List all users (for family management)"""
    # Only allow parents/admins to see all users
    if current_user.role not in [UserRole.PARENT, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    users = db.query(SimpleUser).filter(SimpleUser.is_active == True).all()
    return [
        UserProfile(
            id=user.id,
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            role=user.role.value if user.role else "child",
            first_name=user.first_name,
            last_name=user.last_name,
            ui_language=user.ui_language,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
        )
        for user in users
    ]


@router.post("/logout")
async def logout():
    """Logout user (client should delete token)"""
    return {"message": "Logout successful"}


@router.get("/me")
async def get_current_user_info(
    current_user: Optional[SimpleUser] = Depends(get_current_user),
):
    """Get current user info (no authentication required)"""
    if not current_user:
        return {"authenticated": False, "user": None}

    return {
        "authenticated": True,
        "user": {
            "user_id": current_user.user_id,
            "username": current_user.username,
            "role": current_user.role.value if current_user.role else "child",
        },
    }
