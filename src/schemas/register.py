# from pydantic import BaseModel, Field, ConfigDict
# from datetime import datetime
# from typing import Optional

# class UserBase(BaseModel):
#     username: str = Field(..., min_length=3, max_length=50)
#     email: str = Field(..., min_length=5, max_length=100)
#     full_name: Optional[str] = Field(None, max_length=100)
#     is_active: bool = Field(default=True)

# class UserCreate(UserBase):
#     password: str = Field(..., min_length=8)

# class UserUpdate(BaseModel):
#     username: Optional[str] = Field(None, min_length=3, max_length=50)
#     email: Optional[str] = Field(None, min_length=5, max_length=100)
#     full_name: Optional[str] = Field(None, max_length=100)
#     is_active: Optional[bool] = None
#     password: Optional[str] = Field(None, min_length=8)

# class UserOut(UserBase):
#     id: int
#     created_at: datetime
#     updated_at: datetime

#     model_config = ConfigDict(from_attributes=True)

# src/schemas/user.py
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID   # ← add this
# ────────────────────────────────────────────────
# Base / Shared fields
# ────────────────────────────────────────────────
class UserBase(BaseModel):
    """
    Common fields shared between create, update, and output.
    """
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Unique username (letters, numbers, _, -)"
    )
    email: EmailStr = Field(
        ...,
        max_length=100,
        description="Valid email address"
    )
    full_name: Optional[str] = Field(
        None,
        max_length=100,
        description="User's display name (optional)"
    )


# ────────────────────────────────────────────────
# Create (registration)
# ────────────────────────────────────────────────
class UserCreate(UserBase):
    """
    Schema used when registering a new user.
    """
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User password (will be hashed)"
    )


# ────────────────────────────────────────────────
# Update (PATCH / users/me or admin)
# ────────────────────────────────────────────────
class UserUpdate(BaseModel):
    """
    Fields that can be updated (all optional).
    """
    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$"
    )
    email: Optional[EmailStr] = Field(None, max_length=100)
    full_name: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=8, max_length=128)
    is_active: Optional[bool] = Field(None, description="Admin-only field usually")

    model_config = ConfigDict(
        extra="forbid",           # prevent unknown fields
    )


# ────────────────────────────────────────────────
# Output / Response
# ────────────────────────────────────────────────
class UserOut(UserBase):
    """
    Safe response model (never includes password).
    """
    id: UUID = Field(..., description="Unique user identifier")  # ← changed from int to UUID    # If you switched user.id to UUID, change to:
    # id: UUID = Field(..., description="Unique user identifier")

    created_at: datetime = Field(..., description="Account creation time")
    updated_at: datetime = Field(..., description="Last update time")
    is_active: bool = Field(..., description="Whether account is active")

    model_config = ConfigDict(
        from_attributes=True,           # ORM mode (SQLAlchemy)
        populate_by_name=True,
        json_encoders={
            UUID: str,              # Serialize UUID as string in JSON
            datetime: lambda v: v.isoformat()
        },
        exclude_none=True,              # don't send null fields
    )


# Optional: very common additional variants

class UserOutPrivate(UserOut):
    """
    For admin endpoints or internal use (if you ever expose more fields)
    """
    # e.g. last_login: Optional[datetime]
    pass


class UserMeOut(UserOut):
    """
    Response for /users/me (current user)
    Can include more personal fields if needed
    """
    pass