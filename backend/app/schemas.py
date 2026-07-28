from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID

from app.models import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: UserRole


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    role: UserRole
    created_at: datetime

    model_config = {
        "from_attributes": True
    }