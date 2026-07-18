"""
Фикстуры для pytest
"""

import pytest
import tempfile
import os
from app import create_app
from app.config import config
from app.models.database import get_db_connection, init_database
from PIL import Image
import numpy as np


@pytest.fixture
def app():
    """Создание тестового приложения"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    
    # Используем тестовую БД
    config.DB_CONFIG['database'] = 'postgres_test'
    
    # Создаем тестовую БД
    init_database()
    
    yield app
    
    # Очистка после тестов
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS users CASCADE")
        cur.execute("DROP TABLE IF EXISTS students CASCADE")
        cur.execute("DROP TABLE IF EXISTS schedule_cache CASCADE")
        cur.execute("DROP TABLE IF EXISTS attendance CASCADE")
        conn.commit()


@pytest.fixture
def client(app):
    """Тестовый клиент Flask"""
    return app.test_client()


@pytest.fixture
def db():
    """Фикстура для работы с БД"""
    conn = get_db_connection()
    yield conn
    conn.close()


@pytest.fixture
def test_user(db):
    """Создание тестового пользователя"""
    from app.models.user import create_user
    user = create_user(
        username='test_user',
        password='test_pass123',
        group_name='09.07.14п1',
        full_name='Test User'
    )
    return user


@pytest.fixture
def test_students(db):
    """Создание тестовых студентов"""
    from app.models.student import add_student
    students = [
        'Иванов Иван',
        'Петров Петр',
        'Сидоров Сидор'
    ]
    for name in students:
        add_student(name, '09.07.14п1')
    return students


@pytest.fixture
def test_face_image():
    """Создание тестового изображения лица"""
    img = Image.new('RGB', (160, 160), color='white')
    for i in range(40, 120):
        for j in range(40, 120):
            img.putpixel((i, j), (128, 128, 128))
    
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
        img.save(f.name)
        return f.name


@pytest.fixture
def mock_mtcnn(mocker):
    """Mock для MTCNN"""
    mock = mocker.patch('app.services.face_recognition.mtcnn')
    mock.detect.return_value = (np.array([[10, 10, 150, 150]]), None)
    return mock


@pytest.fixture
def mock_recognition_model(mocker):
    """Mock для модели распознавания"""
    import torch
    mock = mocker.patch('app.services.face_recognition.recognition_model')
    mock.return_value = torch.tensor([0.1] * 512)
    return mock


@pytest.fixture
def mock_face_database(mocker):
    """Mock для базы лиц"""
    import torch
    mock = mocker.patch('app.services.face_recognition.face_database')
    mock.__getitem__.return_value = torch.tensor([0.1] * 512)
    return mock