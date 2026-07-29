from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app import models
from app.schemas import UserCreate, UserResponse
from app.utils.hash import hash_password
from fastapi.security import OAuth2PasswordRequestForm
from app.utils.hash import verify_password
from app.utils.jwt import create_access_token
from app.utils.oauth2 import get_current_user
from app.utils.role_check import role_required


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# register
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = (
        db.query(models.User)
        .filter(models.User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )

    new_user = models.User(
        email=user.email,
        hashed_password=hash_password(user.password),   # Temporary (plain text)
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# login
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = (
        db.query(models.User)
        .filter(models.User.email == form_data.username)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not verify_password(
        form_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    access_token = create_access_token(
        data={
            "user_id": str(user.id),
            "role": user.role.value
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me")
def get_me(
    current_user = Depends(get_current_user)
):
    return current_user




@router.get("/test")
def test_authentication(
    current_user = Depends(get_current_user)
):
    return {
        "message": "You are authenticated"
    }



@router.get("/review")
def review_document(
    current_user: UserResponse = Depends(role_required("reviewer"))
):
    return {
        "message": "Reviewer access granted"
    }
