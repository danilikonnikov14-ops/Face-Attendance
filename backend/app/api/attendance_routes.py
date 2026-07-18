"""
API эндпоинты для посещаемости
"""

from flask import Blueprint, request, jsonify
from PIL import Image
from app.models.student import get_students_by_group
from app.models.attendance import save_attendance_records, get_attendance_by_date, delete_attendance_records
from app.services.face_recognition import process_face, recognize_face, detect_faces, mtcnn
from app.config import config
from app.utils.logger import get_logger
from app.utils.validators import validate_date, validate_pair_number
from datetime import datetime

logger = get_logger(__name__)
attendance_bp = Blueprint('attendance', __name__)


@attendance_bp.route('/recognize_attendance', methods=['POST'])
def recognize_attendance():
    """
    Распознавание лиц и сохранение посещаемости
    
    Request form data:
        group_name: str
        date: str
        pair_number: str
        photo: file
    """
    try:
        # Получение данных
        group_name = request.form.get('group_name', '').strip('"\'')
        date = request.form.get('date', '').strip('"\'')
        pair_number = request.form.get('pair_number', '').strip('"\'')
        photo = request.files.get('photo')
        
        # Валидация
        if not group_name or not date or not pair_number or not photo:
            return jsonify({'error': 'Недостаточно данных'}), 400
        
        if group_name not in config.GROUPS:
            return jsonify({'error': f'Группа {group_name} не найдена'}), 404
        
        # Преобразование даты
        try:
            timestamp_ms = int(date)
            date_obj = datetime.fromtimestamp(timestamp_ms / 1000)
            formatted_date = date_obj.strftime('%Y-%m-%d')
        except:
            formatted_date = date
        
        if not validate_date(formatted_date):
            return jsonify({'error': 'Некорректная дата'}), 400
        
        if not validate_pair_number(pair_number):
            return jsonify({'error': 'Некорректный номер пары'}), 400
        
        # Проверка модели
        if mtcnn is None:
            return jsonify({'error': 'Модель распознавания не загружена'}), 500
        
        # Получение списка студентов
        students = get_students_by_group(group_name)
        if not students:
            return jsonify({'error': f'Нет студентов в группе {group_name}'}), 404
        
        all_students = [s['student_name'] for s in students]
        
        # Распознавание лиц
        recognized_names = set()
        
        try:
            img = Image.open(photo.stream).convert('RGB')
            boxes, _ = detect_faces(img)
            
            if boxes is not None:
                for box in boxes:
                    x1, y1, x2, y2 = [int(c) for c in box]
                    padding = 10
                    face_img = img.crop((
                        max(0, x1 - padding),
                        max(0, y1 - padding),
                        min(img.width, x2 + padding),
                        min(img.height, y2 + padding)
                    ))
                    
                    embedding = process_face(face_img)
                    if embedding is not None:
                        name, similarity = recognize_face(embedding)
                        if name != "Неизвестный":
                            recognized_names.add(name)
                            logger.info(f"✅ Распознан: {name} (схожесть: {similarity:.3f})")
        except Exception as e:
            logger.error(f"❌ Ошибка при распознавании лиц: {e}")
            return jsonify({'error': f'Ошибка при распознавании: {str(e)}'}), 500
        
        # Сохранение посещаемости
        records = []
        for student in all_students:
            status = 'present' if student in recognized_names else 'absent'
            records.append({
                'student_name': student,
                'status': status
            })
        
        # Удаление старых записей
        delete_attendance_records(group_name, formatted_date, pair_number)
        
        # Сохранение новых
        save_attendance_records(group_name, formatted_date, pair_number, records)
        
        return jsonify({
            'success': True,
            'total': len(all_students),
            'present': len(recognized_names),
            'absent': len(all_students) - len(recognized_names),
            'presentList': list(recognized_names),
            'absentList': [s for s in all_students if s not in recognized_names]
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка при распознавании: {e}")
        return jsonify({'error': str(e)}), 500


@attendance_bp.route('/attendance_stats/<group_name>/<date>/<pair_number>', methods=['GET'])
def get_attendance_stats(group_name, date, pair_number):
    """
    Получение статистики посещаемости
    
    Args:
        group_name: Название группы
        date: Дата (YYYY-MM-DD или timestamp)
        pair_number: Номер пары
    """
    try:
        if group_name not in config.GROUPS:
            return jsonify({'error': f'Группа {group_name} не найдена'}), 404
        
        # Преобразование даты
        try:
            if date.isdigit() and len(date) >= 10:
                timestamp_ms = int(date)
                date_obj = datetime.fromtimestamp(timestamp_ms / 1000)
                formatted_date = date_obj.strftime('%Y-%m-%d')
            else:
                formatted_date = date
        except:
            formatted_date = date
        
        # Получение всех студентов
        students = get_students_by_group(group_name)
        all_students = [s['student_name'] for s in students]
        
        # Получение записей посещаемости
        records = get_attendance_by_date(group_name, formatted_date, pair_number)
        attendance_dict = {r['student_name']: r['status'] for r in records}
        
        # Формирование списков
        present_list = []
        absent_list = []
        
        for student in all_students:
            if student in attendance_dict:
                if attendance_dict[student] == 'present':
                    present_list.append(student)
                else:
                    absent_list.append(student)
            else:
                absent_list.append(student)
        
        return jsonify({
            'total': len(all_students),
            'present': len(present_list),
            'absent': len(absent_list),
            'presentList': present_list,
            'absentList': absent_list
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения статистики: {e}")
        return jsonify({'error': str(e)}), 500


@attendance_bp.route('/save_attendance', methods=['POST'])
def save_attendance():
    """
    Сохранение посещаемости вручную
    
    Request body:
        groupName: str
        date: str
        pairNumber: str
        records: list of {studentName, status}
    """
    try:
        data = request.get_json()
        group_name = data.get('groupName')
        date = data.get('date')
        pair_number = data.get('pairNumber')
        records = data.get('records', [])
        
        if not group_name or not date or not pair_number:
            return jsonify({'error': 'Недостаточно данных'}), 400
        
        if group_name not in config.GROUPS:
            return jsonify({'error': f'Группа {group_name} не найдена'}), 404
        
        # Преобразование записей
        formatted_records = []
        for record in records:
            formatted_records.append({
                'student_name': record['studentName'],
                'status': record['status']
            })
        
        # Удаление старых записей
        delete_attendance_records(group_name, date, pair_number)
        
        # Сохранение новых
        save_attendance_records(group_name, date, pair_number, formatted_records)
        
        return jsonify({
            'success': True,
            'message': f'Сохранено {len(records)} записей'
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения посещаемости: {e}")
        return jsonify({'error': str(e)}), 500


@attendance_bp.route('/attendance/<group_name>/<date>', methods=['GET'])
def get_attendance_for_day(group_name, date):
    """
    Получение посещаемости за день по всем парам
    
    Args:
        group_name: Название группы
        date: Дата (YYYY-MM-DD)
    """
    try:
        if group_name not in config.GROUPS:
            return jsonify({'error': f'Группа {group_name} не найдена'}), 404
        
        records = get_attendance_by_date(group_name, date)
        return jsonify(records)
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения посещаемости за день: {e}")
        return jsonify({'error': str(e)}), 500