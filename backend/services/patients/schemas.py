from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date


class PatientUpdate(BaseModel):
    """Update patient profile"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    phone: Optional[str] = Field(None, pattern=r'^\d{10}$')
    dob: Optional[date] = None
    gender: Optional[str] = Field(None, pattern='^(male|female|other)$')
    blood_group: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    medical_history: Optional[str] = None

class PatientResponse(BaseModel):
    id: int
    user_id: int
    username: str
    email: str
    first_name: str
    last_name: str
    full_name: str
    phone: Optional[str] = None
    dob: Optional[str] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    medical_history: Optional[str] = None
    is_active: bool
    created_at: Optional[str] = None