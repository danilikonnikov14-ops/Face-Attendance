"""
Тесты моделей
"""

import pytest
from app.models.student import get_students_by_group, add_student, delete_student
from app.models.attendance import save_attendance_records, get_attendance_by_date, delete_attendance_records


class TestModels:
    """Тесты моделей"""
    
    def test_add_student(self, db):
        """Тест добавления студента"""
        student = add_student("Тестов Тест", "09.07.14п1")
        assert student is not None
        
        with pytest.raises(Exception):
            add_student("Тестов Тест", "09.07.14п1")
    
    def test_get_students(self, db, test_students):
        """Тест получения студентов"""
        students = get_students_by_group("09.07.14п1")
        assert len(students) == 3
        assert "Иванов Иван" in [s['student_name'] for s in students]
        
        students = get_students_by_group("nonexistent")
        assert len(students) == 0
    
    def test_delete_student(self, db):
        """Тест удаления студента"""
        student = add_student("ДляУдаления", "09.07.14п1")
        assert student is not None
        
        result = delete_student("ДляУдаления", "09.07.14п1")
        assert result is True
        
        result = delete_student("ДляУдаления", "09.07.14п1")
        assert result is False
    
    def test_save_attendance(self, db, test_students):
        """Тест сохранения посещаемости"""
        records = [
            {'student_name': 'Иванов Иван', 'status': 'present'},
            {'student_name': 'Петров Петр', 'status': 'absent'},
            {'student_name': 'Сидоров Сидор', 'status': 'present'}
        ]
        
        result = save_attendance_records("09.07.14п1", "2026-01-13", "1", records)
        assert result is True
        
        attendance = get_attendance_by_date("09.07.14п1", "2026-01-13", "1")
        assert len(attendance) == 3
        
        statuses = {r['student_name']: r['status'] for r in attendance}
        assert statuses['Иванов Иван'] == 'present'
        assert statuses['Петров Петр'] == 'absent'