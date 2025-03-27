import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime
from models import ContactInfo

class JSONStorage:
    def __init__(self, file_path: str = "data/contacts.json"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            with open(self.file_path, 'w') as f:
                json.dump([], f)
    
    def save_contact(self, contact: ContactInfo) -> None:
        """Save a single contact to JSON file"""
        contacts = self.load_all_contacts()
        contacts.append(contact.model_dump())
        with open(self.file_path, 'w') as f:
            json.dump(contacts, f, indent=2)
    
    def load_all_contacts(self) -> List[Dict]:
        """Load all contacts from JSON file"""
        with open(self.file_path, 'r') as f:
            return json.load(f)
    
    def get_contacts_by_date(self, date: str) -> List[Dict]:
        """Get contacts with appointments on a specific date"""
        all_contacts = self.load_all_contacts()
        return [c for c in all_contacts if c.get('appointment_date') == date]