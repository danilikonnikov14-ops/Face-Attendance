"""
Инициализация Flask приложения
"""

from flask import Flask, jsonify
from flask_cors import CORS
from app.config import config
from app.utils.logger import setup_logging

def create_app():
    """Фабрика создания Flask приложения"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['DEBUG'] = config.DEBUG
    
    # Настройка CORS
    CORS(app)
    
    # Настройка логирования
    setup_logging(app)
    
    # Регистрация Blueprints
    from app.api.auth_routes import auth_bp
    from app.api.schedule_routes import schedule_bp
    from app.api.students_routes import students_bp
    from app.api.attendance_routes import attendance_bp
    from app.api.stats_routes import stats_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(stats_bp)
    
    # Health check
    @app.route('/health', methods=['GET'])
    def health():
        from app.models.database import get_db_connection
        from app.services.face_recognition import recognition_model, face_database
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT 1")
            db_status = cur.fetchone() is not None
            cur.close()
            conn.close()
        except:
            db_status = False
        
        return jsonify({
            'status': 'ok',
            'app': config.APP_NAME,
            'version': config.VERSION,
            'database': db_status,
            'model_loaded': recognition_model is not None,
            'registered_faces': len(face_database),
            'timestamp': datetime.now().isoformat()
        })
    
    return app

from datetime import datetime