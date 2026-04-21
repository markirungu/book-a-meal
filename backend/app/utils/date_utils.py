from datetime import datetime

def format_date(dt):
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    return dt.strftime("%A, %B %d, %Y")

def format_datetime(dt):
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    return dt.strftime("%A, %B %d, %Y at %I:%M %p")