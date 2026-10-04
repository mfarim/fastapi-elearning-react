from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=4)


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=6)
    nis: str = Field(..., min_length=3)
    nisn: Optional[str] = None
    gender: str = Field(..., pattern="^(L|P|M|F)$")
    classroom_id: Optional[int] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class AuthResponse(BaseModel):
    accessToken: str
    refreshToken: str = ""
    tokenType: str = "Bearer"
    userId: int
    name: str
    email: str
    roles: List[str]
    active: bool = True
    impersonatedBy: Optional[int] = None

    # Pythonic snake_case aliases for direct API flexibility
    token: Optional[str] = None


class UserProfileResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    roles: List[str]
    active: bool = True
    teacher: Optional[Any] = None
    student: Optional[Any] = None
