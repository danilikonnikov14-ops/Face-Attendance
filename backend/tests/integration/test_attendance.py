"""
Интеграционные тесты посещаемости
"""

import pytest
import json
from io import BytesIO
from PIL import Image


class TestAttendance:
    """Тесты логики посещаемости"""
    
    def test_save_attendance(self, client, test_students):
        """Тест сохранения посещаемости"""
        records = [
            {'studentName': 'Иванов Иван', 'status': 'present'},
            {'studentName': 'Петров Петр', 'status': 'absent'},
            {'studentName': 'Сидоров Сидор', 'status': 'present'}
        ]
        
        response = client.post('/save_attendance', json={
            'groupName': '09.07.14п1',
            'date': '2026-01-13',
            'pairNumber': '1',
            'records': records
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_get_attendance_stats(self, client, test_students):
        """Тест получения статистики посещаемости"""
        records = [
            {'studentName': 'Иванов Иван', 'status': 'present'},
            {'studentName': 'Петров Петр', 'status': 'absent'},
            {'studentName': 'Сидоров Сидор', 'status': 'present'}
        ]
        client.post('/save_attendance', json={
            'groupName': '09.07.14п1',
            'date': '2026-01-13',
            'pairNumber': '1',
            'records': records
        })
        
        response = client.get('/attendance_stats/09.07.14п1/2026-01-13/1')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['total'] == 3
        assert data['present'] == 2
        assert data['absent'] == 1
    
    def test_attendance_trend(self, client, test_students):
        """Тест динамики посещаемости"""
        records = [
            {'studentName': 'Иванов Иван', 'status': 'present'},
            {'studentName': 'Петров Петр', 'status': 'present'},
            {'studentName': 'Сидоров Сидор', 'status': 'present'}
        ]
        client.post('/save_attendance', json={
            'groupName': '09.07.14п1',
            'date': '2026-01-13',
            'pairNumber': '1',
            'records': records
        })
        
        response = client.get('/attendance_trend/09.07.14п1?period=week')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'dates' in data
        assert 'rates' in data
    
    def test_student_stats(self, client, test_students):
        """Тест статистики по студентам"""
        records = [
            {'studentName': 'Иванов Иван', 'status': 'present'},
            {'studentName': 'Петров Петр', 'status': 'absent'},
            {'studentName': 'Сидоров Сидор', 'status': 'present'}
        ]
        client.post('/save_attendance', json={
            'groupName': '09.07.14п1',
            'date': '2026-01-13',
            'pairNumber': '1',
            'records': records
        })
        
        response = client.get('/student_stats/09.07.14п1')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data) == 3
        
        ivanov = next(s for s in data if s['name'] == 'Иванов Иван')
        petrov = next(s for s in data if s['name'] == 'Петров Петр')
        assert ivanov['percent'] > petrov['percent']