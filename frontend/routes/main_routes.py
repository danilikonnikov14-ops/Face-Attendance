"""
Главные маршруты (главная страница, статистика, health)
"""

from flask import Blueprint, render_template, jsonify
from config.config import config
from datetime import datetime

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def groups_page():
    """Главная страница - список групп"""
    return render_template('groups.html', groups=config.GROUPS)


@main_bp.route('/statistics/<group_name>')
def statistics_page(group_name):
    """Страница статистики группы"""
    if group_name not in config.GROUPS:
        return render_template('404.html'), 404
    return render_template('statistics.html', group_name=group_name)


@main_bp.route('/health')
def health():
    """Проверка статуса приложения"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'api_url': config.API_BASE_URL
    })