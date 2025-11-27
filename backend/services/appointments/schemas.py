from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date


class AppointmentCreate(BaseModel):
    doctor_id: int
    appointment_date: date
    appointment_time: str = Field(..., pattern=r'^\d{2}:\d{2}$')
    booking_notes: Optional[str] = None

    @field_validator('appointment_date')
    @classmethod
    def validate_date(cls, v):
        if v < date.today():
            raise ValueError('Cannot book past dates')
        return v


class AppointmentUpdate(BaseModel):
    appointment_date: date
    appointment_time: str = Field(..., pattern=r'^\d{2}:\d{2}$')