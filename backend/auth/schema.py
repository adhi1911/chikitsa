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