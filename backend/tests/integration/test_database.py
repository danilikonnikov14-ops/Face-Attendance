"""
Интеграционные тесты базы данных
"""

import pytest
from app.models.database import get_db_connection, init_database
from app.models.user import create_user, get_user_by_username, update_user, delete_user
from app.models.student import add_student, get_students_by_group, delete_student, get_all_groups
from app.models.attendance import save_attendance_records, get_attendance_by_date, get_attendance_stats, delete_attendance_records
from app.models.schedule import save_schedule, get_schedule, clear_schedule


class TestDatabase:
    """Тесты базы данных"""
    
    def test_database_connection(self, db):
        """Тест подключения к БД"""
        assert db is not None
        cur = db.cursor()
        cur.execute("SELECT 1")
        result = cur.fetchone()
        assert result is not None
        cur.close()
    
    def test_database_init(self):
        """Тест инициализации БД"""
        result = init_database()
        assert result is True
        
        # Проверка создания таблиц
        conn = get_db_connection()
        cur = conn.cursor()
        
        tables = ['users', 'students', 'schedule_cache', 'attendance']
        for table in tables:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                )
            """, (table,))
            exists = cur.fetchone()['exists']
            assert exists is True, f"Таблица {table} не создана"
        
        cur.close()
        conn.close()
    
    def test_user_crud(self, db):
        """Тест CRUD операций с пользователями"""
        # Создание
        user = create_user(
            username="crud_test",
            password="test123",
            group_name="09.07.14п1",
            full_name="CRUD Test User"
        )
        assert user is not None
        assert user['username'] == "crud_test"
        
        # Чтение
        found = get_user_by_username("crud_test")
        assert found is not None
        assert found['full_name'] == "CRUD Test User"
        
        # Обновление
        updated = update_user("crud_test", full_name="Updated Name", group_name="09.07.14п2")
        assert updated is not None
        assert updated['full_name'] == "Updated Name"
        assert updated['group_name'] == "09.07.14п2"
        
        # Удаление
        deleted = delete_user("crud_test")
        assert deleted is True
        
        # Проверка удаления
        gone = get_user_by_username("crud_test")
        assert gone is None
    
    def test_student_crud(self, db):
        """Тест CRUD операций со студентами"""
        # Создание
        student = add_student("Тестов Тестович", "09.07.14п1")
        assert student is not None
        assert student['student_name'] == "Тестов Тестович"
        
        # Чтение
        students = get_students_by_group("09.07.14п1")
        assert len(students) > 0
        assert "Тестов Тестович" in [s['student_name'] for s in students]
        
        # Получение всех групп
        groups = get_all_groups()
        assert "09.07.14п1" in groups
        
        # Удаление
        deleted = delete_student("Тестов Тестович", "09.07.14п1")
        assert deleted is True
        
        # Проверка удаления
        students = get_students_by_group("09.07.14п1")
        assert "Тестов Тестович" not in [s['student_name'] for s in students]
    
    def test_attendance_crud(self, db, test_students):
        """Тест CRUD операций с посещаемостью"""
        # Создание записей
        records = [
            {'student_name': 'Иванов Иван', 'status': 'present'},
            {'student_name': 'Петров Петр', 'status': 'absent'},
            {'student_name': 'Сидоров Сидор', 'status': 'present'}
        ]
        
        result = save_attendance_records(
            "09.07.14п1",
            "2026-01-13",
            "1",
            records
        )
        assert result is True
        
        # Чтение
        attendance = get_attendance_by_date("09.07.14п1", "2026-01-13", "1")
        assert len(attendance) == 3
        
        statuses = {r['student_name']: r['status'] for r in attendance}
        assert statuses['Иванов Иван'] == 'present'
        assert statuses['Петров Петр'] == 'absent'
        assert statuses['Сидоров Сидор'] == 'present'
        
        # Статистика
        stats = get_attendance_stats("09.07.14п1")
        assert len(stats) == 3
        
        for stat in stats:
            if stat['student_name'] == 'Иванов Иван':
                assert stat['present_count'] == 1
                assert stat['total_pairs'] == 1
            elif stat['student_name'] == 'Петров Петр':
                assert stat['present_count'] == 0
                assert stat['total_pairs'] == 1
        
        # Удаление
        deleted = delete_attendance_records("09.07.14п1", "2026-01-13", "1")
        assert deleted == 3
        
        # Проверка удаления
        attendance = get_attendance_by_date("09.07.14п1", "2026-01-13", "1")
        assert len(attendance) == 0
    
    def test_attendance_update(self, db, test_students):
        """Тест обновления записей посещаемости"""
        # Первое сохранение
        records1 = [
            {'student_name': 'Иванов Иван', 'status': 'present'},
            {'student_name': 'Петров Петр', 'status': 'absent'}
        ]
        save_attendance_records("09.07.14п1", "2026-01-14", "2", records1)
        
        # Проверка
        attendance = get_attendance_by_date("09.07.14п1", "2026-01-14", "2")
        assert len(attendance) == 2
        statuses = {r['student_name']: r['status'] for r in attendance}
        assert statuses['Иванов Иван'] == 'present'
        assert statuses['Петров Петр'] == 'absent'
        
        # Обновление (изменяем статус Петрова)
        records2 = [
            {'student_name': 'Иванов Иван', 'status': 'present'},
            {'student_name': 'Петров Петр', 'status': 'present'}
        ]
        save_attendance_records("09.07.14п1", "2026-01-14", "2", records2)
        
        # Проверка обновления
        attendance = get_attendance_by_date("09.07.14п1", "2026-01-14", "2")
        statuses = {r['student_name']: r['status'] for r in attendance}
        assert statuses['Иванов Иван'] == 'present'
        assert statuses['Петров Петр'] == 'present'
    
    def test_schedule_crud(self, db):
        """Тест CRUD операций с расписанием"""
        # Создание расписания
        days = [
            {
                'name': 'Понедельник',
                'date': '2026-01-13',
                'classes': [
                    {
                        'number': '1',
                        'time': '08:30-10:00',
                        'subject': 'Математика',
                        'teacher': 'Иванов И.И.',
                        'room': '101'
                    },
                    {
                        'number': '2',
                        'time': '10:15-11:45',
                        'subject': 'Физика',
                        'teacher': 'Петров П.П.',
                        'room': '102'
                    }
                ]
            },
            {
                'name': 'Вторник',
                'date': '2026-01-14',
                'classes': [
                    {
                        'number': '1',
                        'time': '08:30-10:00',
                        'subject': 'Химия',
                        'teacher': 'Козлова К.К.',
                        'room': '201'
                    }
                ]
            }
        ]
        
        saved = save_schedule("09.07.14п1", days)
        assert saved == 3  # 3 пары всего
        
        # Чтение
        schedule = get_schedule("09.07.14п1")
        assert len(schedule) == 2  # 2 дня
        
        # Проверка данных
        monday = next(d for d in schedule if d['name'] == 'Понедельник')
        assert len(monday['classes']) == 2
        assert monday['classes'][0]['subject'] == 'Математика'
        assert monday['classes'][1]['subject'] == 'Физика'
        
        tuesday = next(d for d in schedule if d['name'] == 'Вторник')
        assert len(tuesday['classes']) == 1
        assert tuesday['classes'][0]['subject'] == 'Химия'
        
        # Очистка
        cleared = clear_schedule("09.07.14п1")
        assert cleared == 3
        
        # Проверка очистки
        schedule = get_schedule("09.07.14п1")
        assert len(schedule) == 0
    
    def test_schedule_update(self, db):
        """Тест обновления расписания"""
        # Первое сохранение
        days1 = [
            {
                'name': 'Понедельник',
                'date': '2026-01-13',
                'classes': [
                    {
                        'number': '1',
                        'time': '08:30-10:00',
                        'subject': 'Старое',
                        'teacher': 'Старый',
                        'room': '101'
                    }
                ]
            }
        ]
        save_schedule("09.07.14п1", days1)
        
        # Проверка
        schedule = get_schedule("09.07.14п1")
        assert schedule[0]['classes'][0]['subject'] == 'Старое'
        
        # Обновление
        days2 = [
            {
                'name': 'Понедельник',
                'date': '2026-01-13',
                'classes': [
                    {
                        'number': '1',
                        'time': '08:30-10:00',
                        'subject': 'Новое',
                        'teacher': 'Новый',
                        'room': '102'
                    }
                ]
            }
        ]
        save_schedule("09.07.14п1", days2)
        
        # Проверка обновления
        schedule = get_schedule("09.07.14п1")
        assert schedule[0]['classes'][0]['subject'] == 'Новое'
        assert schedule[0]['classes'][0]['teacher'] == 'Новый'
        assert schedule[0]['classes'][0]['room'] == '102'
    
    def test_multiple_groups(self, db):
        """Тест работы с несколькими группами"""
        # Добавляем студентов в разные группы
        add_student("Студент1", "09.07.14п1")
        add_student("Студент2", "09.07.14п1")
        add_student("Студент3", "09.07.14п2")
        
        # Проверка
        students1 = get_students_by_group("09.07.14п1")
        assert len(students1) == 2
        
        students2 = get_students_by_group("09.07.14п2")
        assert len(students2) == 1
        
        # Сохраняем посещаемость для разных групп
        records1 = [{'student_name': 'Студент1', 'status': 'present'}]
        save_attendance_records("09.07.14п1", "2026-01-13", "1", records1)
        
        records2 = [{'student_name': 'Студент3', 'status': 'absent'}]
        save_attendance_records("09.07.14п2", "2026-01-13", "1", records2)
        
        # Проверка
        att1 = get_attendance_by_date("09.07.14п1", "2026-01-13", "1")
        assert len(att1) == 1
        assert att1[0]['status'] == 'present'
        
        att2 = get_attendance_by_date("09.07.14п2", "2026-01-13", "1")
        assert len(att2) == 1
        assert att2[0]['status'] == 'absent'
    
    def test_duplicate_constraints(self, db):
        """Тест проверки уникальности (дубликаты)"""
        # Дубликат студента в одной группе
        add_student("Дубликат", "09.07.14п1")
        with pytest.raises(Exception):
            add_student("Дубликат", "09.07.14п1")
        
        # Но можно в другой группе
        student = add_student("Дубликат", "09.07.14п2")
        assert student is not None
        
        # Дубликат посещаемости
        records = [{'student_name': 'Дубликат', 'status': 'present'}]
        save_attendance_records("09.07.14п1", "2026-01-13", "1", records)
        # Повторное сохранение должно обновить, а не создать дубликат
        records2 = [{'student_name': 'Дубликат', 'status': 'absent'}]
        save_attendance_records("09.07.14п1", "2026-01-13", "1", records2)
        
        att = get_attendance_by_date("09.07.14п1", "2026-01-13", "1")
        assert len(att) == 1
        assert att[0]['status'] == 'absent'
    
    def test_transaction_rollback(self, db):
        """Тест отката транзакции при ошибке"""
        # Создаем студента
        add_student("Транзакция", "09.07.14п1")
        
        # Попытка создать дубликат должна откатить транзакцию
        try:
            add_student("Транзакция", "09.07.14п1")
        except Exception:
            pass
        
        # Проверяем, что первый студент все еще существует
        students = get_students_by_group("09.07.14п1")
        assert "Транзакция" in [s['student_name'] for s in students]
    
    def test_bulk_insert(self, db):
        """Тест массовой вставки"""
        # Добавляем много студентов
        students = [f"Студент_{i}" for i in range(10)]
        for name in students:
            add_student(name, "09.07.14п1")
        
        # Проверка
        all_students = get_students_by_group("09.07.14п1")
        assert len(all_students) >= 10
        
        # Массовое сохранение посещаемости
        records = [
            {'student_name': name, 'status': 'present' if i % 2 == 0 else 'absent'}
            for i, name in enumerate(students)
        ]
        save_attendance_records("09.07.14п1", "2026-01-15", "3", records)
        
        # Проверка
        att = get_attendance_by_date("09.07.14п1", "2026-01-15", "3")
        assert len(att) == 10
        
        present_count = sum(1 for r in att if r['status'] == 'present')
        assert present_count == 5  # Половина присутствует
    
    def test_cleanup_after_tests(self, db):
        """Очистка после тестов"""
        # Удаляем все созданные данные
        delete_attendance_records("09.07.14п1")
        clear_schedule("09.07.14п1")
        
        # Проверяем, что данные удалены
        att = get_attendance_by_date("09.07.14п1", "2026-01-15", "3")
        assert len(att) == 0
        
        schedule = get_schedule("09.07.14п1")
        assert len(schedule) == 0