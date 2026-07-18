"""
API эндпоинты для студентов
"""

from flask import Blueprint, request, jsonify
from app.models.student import get_students_by_group, add_student, delete_student
from app.config import config
from app.utils.logger import get_logger
from app.utils.validators import validate_student_name

logger = get_logger(__name__)
students_bp = Blueprint('students', __name__)


@students_bp.route('/students/<group_name>', methods=['GET'])
def get_students(group_name):
    """
    Получение списка студентов группы
    
    Args:
        group_name: Название группы
    """
    try:
        if group_name not in config.GROUPS:
            return jsonify({'error': f'Группа {group_name} не найдена'}), 404
        
        students = get_students_by_group(group_name)
        return jsonify([{'name': s['student_name']} for s in students])
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения студентов: {e}")
        return jsonify({'error': str(e)}), 500


@students_bp.route('/students/<group_name>', methods=['POST'])
def add_student_to_group(group_name):
    """
    Добавление студента в группу
    
    Request body:
        student_name: str
    """
    try:
        data = request.get_json()
        student_name = data.get('student_name')
        
        if not student_name or not validate_student_name(student_name):
            return jsonify({'error': 'Некорректное имя студента'}), 400
        
        if group_name not in config.GROUPS:
            return jsonify({'error': f'Группа {group_name} не найдена'}), 404
        
        result = add_student(student_name, group_name)
        return jsonify({'success': True, 'student': result})
        
    except Exception as e:
        logger.error(f"❌ Ошибка добавления студента: {e}")
        return jsonify({'error': str(e)}), 500


@students_bp.route('/students/<group_name>/<student_name>', methods=['DELETE'])
def delete_student_from_group(group_name, student_name):
    """
    Удаление студента из группы
    
    Args:
        group_name: Название группы
        student_name: Имя студента
    """
    try:
        if group_name not in config.GROUPS:
            return jsonify({'error': f'Группа {group_name} не найдена'}), 404
        
        result = delete_student(student_name, group_name)
        
        if result:
            return jsonify({'success': True, 'message': f'Студент {student_name} удален'})
        else:
            return jsonify({'error': 'Студент не найден'}), 404
            
    except Exception as e:
        logger.error(f"❌ Ошибка удаления студента: {e}")
        return jsonify({'error': str(e)}), 500