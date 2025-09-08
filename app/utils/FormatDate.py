from typing import Optional
from datetime import datetime

def format_date(date: Optional[datetime]) -> Optional[str]:
    return date.strftime("%d-%m-%Y %H:%M:%S") if date else None