# User model - placeholder for future database integration
from typing import Dict, List

def create_user(email: str, password_hash: str, name: str, account_type: str = 'owner') -> Dict:
    return {
        'email': email,
        'password': password_hash,
        'name': name,
        'accountType': account_type,
        'vehicles': [],
        'emailVerified': True
    }