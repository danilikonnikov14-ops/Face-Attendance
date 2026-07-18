"""
Конфигурация веб-приложения
"""

import os
from dotenv import load_dotenv

# Загрузка .env
load_dotenv()


class Config:
    """Класс конфигурации"""
    
    # API
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://82.23.177.102:5000')
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', 10))
    
    # Flask
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_PORT', 5001))
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Группы
    GROUPS = ["09.07.14п1", "09.07.14п2", "09.07.14р"]
    
    # Настройки кэширования
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'False').lower() == 'true'
    CACHE_TTL = int(os.getenv('CACHE_TTL', 300))  # 5 минут


config = Config()