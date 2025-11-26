from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional

class LoginSchema(BaseModel):
    username: str 
    password: str 
    role: str


class RegisterPatient(BaseModel):
    username: str = Field(...,min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(...,min_length=8)
    first_name: str
    last_name: str
    dob: date
    gender: str = Field(...,pattern='^(male|female|other)$')
    blood_group: Optional[str]
    phone: str = Field(...,pattern='^\d{10}$')
    address: Optional[str]
    emergency_contact_name: Optional[str]
    emergency_contact_phone: Optional[str]
    medical_history: Optional[str]


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class UpdateProfileSchema(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    medical_history: Optional[str] = None
    specialization: Optional[str] = None


class UserProfileResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: Optional[str] = None
    last_login: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    medical_history: Optional[str] = None
    specialization: Optional[str] = None
    license_number: Optional[str] = None
    department_id: Optional[int] = None

    ## doctor fields
    department_id: Optional[int] = None
    qualification: Optional[str] = None
    experience_years: Optional[int] = None
    consultation_fee: Optional[float] = None
    is_available: Optional[bool] = None

    