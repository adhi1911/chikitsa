from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import date 


## dept schemas ##
class DepartmentBase(BaseModel):
    name: str = Field(...,min_length=2, max_length=100)
    description: Optional[str] = None

class DepartmentCreate(DepartmentBase):
    pass 

class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None,min_length=2, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = True

class DepartmentResponse(DepartmentBase):
    id: int
    is_active: bool
    created_at: date
    updated_at: Optional[date] = None
    total_doctors: Optional[int] = 0


## doctor schemas ##
class DoctorBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    department_id: Optional[int] = None
    email: EmailStr
    phone: str = Field(..., min_length=7, max_length=15)
    specialization: str = Field(..., min_length=2, max_length=100)
    qualification: str
    experience_years: Optional[int] = None  
    consultation_fee: Optional[float] = None

class DoctorCreate(DoctorBase):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

class DoctorUpdate(DoctorBase):
    is_available: Optional[bool] = True

class DoctorResponse(DoctorBase):
    id: int 
    is_available: bool
    department_name: Optional[str] = None


## patient schemas ##

class PatientBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    dob: Optional[date]