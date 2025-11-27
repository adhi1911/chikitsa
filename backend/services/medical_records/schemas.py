from pydantic import BaseModel, Field 
from typing import Optional, List 
from datetime import date

###### PRESCRIPTION SCHEMAS ######
class PrescriptionItemCreate(BaseModel):
    medicine_name: str = Field(..., min_length=1, max_length=100)
    dosage: Optional[str] = Field(None, max_length=50)          
    frequency: Optional[str] = Field(None, max_length=50)       
    duration: Optional[str] = Field(None, max_length=50)        
    instructions: Optional[str] = Field(None, max_length=255) 

class PrescriptionItemUpdate(BaseModel):
    medicine_name: Optional[str] = Field(None, min_length=1, max_length=100)
    dosage: Optional[str] = Field(None, max_length=50)
    frequency: Optional[str] = Field(None, max_length=50)
    duration: Optional[str] = Field(None, max_length=50)
    instructions: Optional[str] = Field(None, max_length=255)



class MedicalRecordCreate(BaseModel):
    diagnosis: str = Field(..., min_length=1, max_length=500)
    symptoms: Optional[str] = Field(None, max_length=500)
    treatment_notes: Optional[str] = None
    doctor_notes: Optional[str] = None        # only for doctors
    followup_date: Optional[date] = None
    prescription_items: Optional[List[PrescriptionItemCreate]] = []


class MedicalRecordUpdate(BaseModel):
    diagnosis: Optional[str] = Field(None, min_length=1, max_length=500)
    symptoms: Optional[str] = Field(None, max_length=500)
    treatment_notes: Optional[str] = None
    doctor_notes: Optional[str] = None
    followup_date: Optional[date] = None


