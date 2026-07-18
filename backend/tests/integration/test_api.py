"""
Интеграционные тесты API
"""

import pytest
import json
from io import BytesIO
from PIL import Image


class TestAPI:
    """Интеграционные тесты API"""
    
    def test_login_success(self, client, test_user):
        """Тест успешного входа"""
        response = client.post('/login', json={
            'username': 'test_user',
            'password': 'test_pass123'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['user']['username'] == 'test_user'
    
    def test_login_fail(self, client):
        """Тест неудачного входа"""
        response = client.post('/login', json={
            'username': 'wrong',
            'password': 'wrong'
        })
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_login_missing_data(self, client):
        """Тест входа без данных"""
        response = client.post('/login', json={})
        assert response.status_code == 400
    
    def test_get_schedule(self, client, db):
        """Тест получения расписания"""
        from app.models.schedule import save_schedule
        
        test_days = [{
            'name': 'Понедельник',
            'date': '2026-01-13',
            'classes': [{
                'number': '1',
                'time': '08:30-10:00',
                'subject': 'Тест',
                'teacher': 'Тестов',
                'room': '101'
            }]
        }]
        save_schedule('09.07.14п1', test_days)
        
        response = client.get('/schedule/09.07.14п1')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data) > 0
        assert data[0]['classes'][0]['subject'] == 'Тест'
    
    def test_get_students(self, client, test_students):
        """Тест получения студентов"""
        response = client.get('/students/09.07.14п1')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data) == 3
        assert data[0]['name'] == 'Иванов Иван'
    
    def test_health_check(self, client):
        """Тест проверки здоровья"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'ok'
        assert 'database' in data
        assert 'timestamp' in data