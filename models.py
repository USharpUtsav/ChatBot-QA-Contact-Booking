from pydantic import BaseModel, EmailStr, validator, ValidationError
import phonenumbers
import dateparser
from typing import Optional
from datetime import datetime
import re
from dateutil.relativedelta import relativedelta, SU, MO, TU, WE, TH, FR, SA

class ContactInfo(BaseModel):
    name: str
    email: EmailStr
    phone: str
    appointment_date: Optional[str] = None
    
    @validator('phone')
    def validate_phone(cls, v):
        try:
            # First clean the input - remove all non-digit characters except leading +
            cleaned = re.sub(r'(?!^\+)[^\d]', '', v)
            
            # Parse the cleaned number
            parsed = phonenumbers.parse(cleaned, None)
            
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError("Invalid phone number")
                
            # Return in E164 format
            return phonenumbers.format_number(
                parsed, 
                phonenumbers.PhoneNumberFormat.E164
            )
        except Exception as e:
            raise ValueError("Please provide a valid international phone number with country code (e.g.+9779828126222)")
    
    @validator('appointment_date', pre=True)
    def parse_date(cls, v):
        if not v:
            return None
        
        # Check for "next <day>"
        match = re.match(r'next (\w+)', v, re.IGNORECASE)
        if match:
            day_name = match.group(1).capitalize()
            days_mapping = {
                "Monday": MO, "Tuesday": TU, "Wednesday": WE,
                "Thursday": TH, "Friday": FR, "Saturday": SA, "Sunday": SU
            }
            if day_name in days_mapping:
                today = datetime.today()
                next_day = today + relativedelta(weekday=days_mapping[day_name](+1))
                return next_day.strftime("%Y-%m-%d")
        
        # Use dateparser as a fallback
        dt = dateparser.parse(v, languages=['en'], settings={'PREFER_DATES_FROM': 'future'})  
        if not dt:
            raise ValueError("Could not understand the date. Try formats like 'next Monday' or '2024-06-15'")
        return dt.strftime("%Y-%m-%d")