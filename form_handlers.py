from models import ContactInfo
from typing import Dict, Optional, List
from enum import Enum
from pydantic import ValidationError  
from storage import JSONStorage  

class FormType(Enum):
    CONTACT = "contact"
    APPOINTMENT = "appointment"

class FormState:

    def __init__(self):
        self.current_form: Optional[FormType] = None
        self.collected_data: Dict[str, str] = {}
        self.required_fields: List[str] = []
        self.current_field_index: int = 0
    
    def reset(self):
        self.__init__()

class FormHandler:
    def __init__(self):
        self.state = FormState()
        self.storage = JSONStorage()
    
    def start_form(self, form_type: FormType) -> str:
        """Initialize a new form"""
        self.state.reset()
        self.state.current_form = form_type
        
        if form_type == FormType.CONTACT:
            self.state.required_fields = ["name", "email", "phone"]
            return "Let's get your contact details. What's your full name?"
        else:  # APPOINTMENT
            self.state.required_fields = ["name", "email", "phone", "appointment_date"]
            return "Let's schedule an appointment. What's your full name?"
    
    def process_input(self, user_input: str) -> Dict:
        """Process user input with immediate validation"""
        if not self.state.current_form:
            return {"error": "No active form"}
        
        current_field = self.state.required_fields[self.state.current_field_index]
        
        try:
            # Create temp data to validate
            temp_data = self.state.collected_data.copy()
            temp_data[current_field] = user_input
            
            # Validate immediately
            if current_field == "email":
                ContactInfo(**{**temp_data, "phone": "+9779828226142", "appointment_date": None})
            elif current_field == "phone":
                ContactInfo(**{**temp_data, "email": "test@example.com", "appointment_date": None})
            else:
                ContactInfo(**{**temp_data, "email": "test@example.com", "phone": "+9779828226142"})
            
            # If validation passed, store the value
            self.state.collected_data[current_field] = user_input
            
            # Move to next field or complete
            if self.state.current_field_index < len(self.state.required_fields) - 1:
                self.state.current_field_index += 1
                next_field = self.state.required_fields[self.state.current_field_index]
                return {
                    "status": "in_progress",
                    "next_field": next_field,
                    "prompt": self._get_field_prompt(next_field)
                }
            else:
                contact_info = ContactInfo(**self.state.collected_data)
                response = {
                    "status": "complete",
                    "data": contact_info,
                    "message": self._generate_success_message(contact_info)
                }
                self.state.reset()
                return response
                
        except ValidationError as e:
            error_msg = str(e.errors()[0]['msg'])
            return {
                "status": "error",
                "error": error_msg,
                "field": current_field,
                "prompt": f"Invalid {current_field}. {error_msg} Please try again:"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "field": current_field,
                "prompt": f"Invalid input. Please try again:"
            }
    
    def _get_field_prompt(self, field: str) -> str:
        """Get the appropriate prompt for each field"""
        prompts = {
            "name": "What's your full name?",
            "email": "What's your email address? (e.g., name@example.com)",
            "phone": "What's your phone number with country code? (e.g., +9779828026222)",
            "appointment_date": "When would you like to schedule? (e.g., 'next Monday' or '2024-06-15')"
        }
        return prompts.get(field, f"Please provide your {field}")
    
    def _generate_success_message(self, contact_info: ContactInfo) -> str:
        """Generate completion message and save data"""
        # Save to JSON storage
        self.storage.save_contact(contact_info)
        
        if self.state.current_form == FormType.APPOINTMENT:
            return (
                f"Appointment scheduled!\n"
                f"Name: {contact_info.name}\n"
                f"Date: {contact_info.appointment_date}\n"
                f"We'll contact you at {contact_info.phone} to confirm.\n"
                f"Your information has been saved."
            )
        else:
            return (
                f"Thank you, {contact_info.name}!\n"
                f"We'll contact you shortly at {contact_info.phone}.\n"
                f"Your information has been saved."
            )