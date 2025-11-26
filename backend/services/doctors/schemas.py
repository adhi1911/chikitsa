
from pydantic import BaseModel, Field, field_validator 
from typing import Optional, List
from datetime import datetime , time 

DAY_NAMES = {
    0: "Monday",
    1: "Tuesday", 
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday"
}


########## Working Hour Schemas ############

class WorkingHoursDay(BaseModel):
    """Single day working hours"""
    day_of_week: int = Field(..., ge=0, le=6)  # 0=Mon, 6=Sun
    start_time: str = Field(..., pattern=r'^\d{2}:\d{2}$')  
    end_time: str = Field(..., pattern=r'^\d{2}:\d{2}$')    

    @field_validator('end_time')
    def end_after_start(cls, v, info):
        start = info.data.get('start_time')
        if start and v <= start:
            raise ValueError('end_time must be after start_time')
        return v



class WorkingHoursCreate(BaseModel):
    """Create working hours for entire week"""
    schedule: List[WorkingHoursDay]

    @field_validator('schedule')
    @classmethod
    def validate_schedule(cls, v):
        if not v:
            raise ValueError('Schedule cannot be empty')

        # Check for duplicate days
        days = [day.day_of_week for day in v]
        if len(days) != len(set(days)):
            raise ValueError('Duplicate days not allowed')

        return v


class WorkingHoursDayUpdate(BaseModel):
    """Update single day working hours"""
    start_time: Optional[str] = Field(None, pattern=r'^\d{2}:\d{2}$')
    end_time: Optional[str] = Field(None, pattern=r'^\d{2}:\d{2}$')
    is_active: Optional[bool] = None



class WorkingHoursBulkUpdate(BaseModel):
    """Bulk update working hourse for entire week"""
    schedule: List[WorkingHoursDay]



class WorkingHoursResponse(BaseModel):
    """Response for single day"""
    id: int
    doctor_id: int
    day_of_week: int
    day_name: str
    start_time: str
    end_time: str
    is_active: bool


########### UNAVAILABILITY SCHEMAS ###########


class WorkingHoursListResponse(BaseModel):
    """Response for full week schedule"""
    doctor_id: int
    schedule: List[WorkingHoursResponse]



class UnavailabilityCreate(BaseModel):
    """Create unavailability period"""
    start_datetime: datetime
    end_datetime: datetime
    reason: Optional[str] = Field(None, max_length=255)

    @field_validator('end_datetime')
    @classmethod
    def end_after_start(cls, v, info):
        start = info.data.get('start_datetime')
        if start and v <= start:
            raise ValueError('end_datetime must be after start_datetime')
        return v

    @field_validator('start_datetime')
    @classmethod
    def not_in_past(cls, v):
        if v < datetime.now():
            raise ValueError('start_datetime cannot be in the past')
        return v


class UnavailabilityUpdate(BaseModel):
    """Update unavailability period"""
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    reason: Optional[str] = Field(None, max_length=255)


class UnavailabilityResponse(BaseModel):
    """Response for unavailability"""
    id: int
    doctor_id: int
    start_datetime: str
    end_datetime: str
    reason: Optional[str] = None
    created_at: Optional[str] = None
