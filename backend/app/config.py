"""
Конфигурация приложения
"""

import os
from dotenv import load_dotenv

# Загрузка .env файла
load_dotenv()

class Config:
    """Класс конфигурации"""
    
    # Информация о приложении
    APP_NAME = "Server Face Attedance"
    VERSION = "1.0.0"
    
    # База данных
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME', 'postgres'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', ''),
        'port': os.getenv('DB_PORT', '5432')
    }
    
    # Группы
    GROUPS_RAW = os.getenv('GROUPS', '')
    GROUPS = [g.strip() for g in GROUPS_RAW.split(',') if g.strip()]
    
    # Пути к моделям
    MODEL_PATH = os.getenv('MODEL_PATH', 'models/face_recognition_model.pth')
    
    # Flask настройки
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_PORT', 5000))
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Настройки расписания
    SCHEDULE_UPDATE_INTERVAL = int(os.getenv('SCHEDULE_UPDATE_INTERVAL', 3600))
    
    # Путь к логам
    LOG_DIR = 'logs'
    LOG_FILE = 'logs/server.log'

# Глобальный объект конфига
config = Config()