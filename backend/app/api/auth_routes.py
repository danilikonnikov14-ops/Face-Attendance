"""
API эндпоинты для аутентификации
"""

from flask import Blueprint, request, jsonify
from app.models.user import authenticate_user
from app.utils.logger import get_logger

logger = get_logger(__name__)
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Вход в систему
    
    Request body:
        username: str
        password: str
    
    Returns:
        success: bool
        user: dict
        message: str (при ошибке)
    """
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Логин и пароль обязательны'
            }), 400
        
        user = authenticate_user(username, password)
        
        if user:
            logger.info(f"✅ Успешный вход: {username}")
            return jsonify({
                'success': True,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'groupName': user['group_name'],
                    'fullName': user['full_name']
                }
            })
        
        logger.warning(f"⚠️ Неудачная попытка входа: {username}")
        return jsonify({
            'success': False,
            'message': 'Неверный логин или пароль'
        }), 401
        
    except Exception as e:
        logger.error(f"❌ Ошибка при входе: {e}")
        return jsonify({
            'success': False,
            'message': 'Внутренняя ошибка сервера'
        }), 500