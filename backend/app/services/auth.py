"""
Сервис аутентификации - хеширование и проверка паролей
"""

import hashlib

def hash_password(password: str) -> str:
    """Хеширование пароля с использованием SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Проверка пароля"""
    return hash_password(password) == hashed

def generate_token(user_id: int, username: str) -> str:
    """Генерация простого токена (для будущего использования)"""
    import time
    import hmac
    import os
    
    secret = os.getenv('SECRET_KEY', 'dev-secret-key')
    data = f"{user_id}:{username}:{int(time.time())}"
    token = hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()
    
    return token