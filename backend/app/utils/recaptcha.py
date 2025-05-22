import requests
from typing import Optional
from app.config import settings

def verify_recaptcha(token: str) -> bool:
    if not settings.VITE_RECAPTCHA_ENABLED:
        return True
    
    response = requests.post(
        'https://www.google.com/recaptcha/api/siteverify',
        data={
            'secret': settings.VITE_RECAPTCHA_SITE_KEY,
            'response': token
        }
    )
    result = response.json()
    return result.get('success', False)
