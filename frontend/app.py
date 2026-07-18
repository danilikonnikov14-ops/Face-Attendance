"""
Web Site Face Attendance
Веб-интерфейс для системы распознавания лиц
"""

from flask import Flask
from flask import render_template, request, jsonify
import requests
from datetime import datetime
import os

app = Flask(__name__)

# Конфигурация
API_BASE_URL = os.getenv('API_BASE_URL', 'http://82.23.177.102:5000')
GROUPS = ["09.07.14п1", "09.07.14п2", "09.07.14р"]

def get_api_data(endpoint):
    """Запрос к API"""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Ошибка API: {e}")
        return None

# Маршруты
@app.route('/')
def groups_page():
    return render_template('groups.html', groups=GROUPS)

@app.route('/<group_name>.html')
def group_schedule(group_name):
    if group_name not in GROUPS:
        return render_template('404.html'), 404
    schedule = get_api_data(f"/schedule/{group_name}") or []
    return render_template('group.html', group_name=group_name, schedule=schedule)

@app.route('/lesson/<group_name>/<date>/<pair_number>')
def lesson_details(group_name, date, pair_number):
    if group_name not in GROUPS:
        return render_template('404.html'), 404
    
    schedule = get_api_data(f"/schedule/{group_name}") or []
    lesson = None
    day_name = ""
    
    for day in schedule:
        for cls in day.get('classes', []):
            if cls.get('number') == pair_number:
                lesson = cls
                day_name = day.get('name', '')
                break
        if lesson:
            break
    
    if not lesson:
        return render_template('404.html'), 404
    
    stats_data = get_api_data(f"/attendance_stats/{group_name}/{date}/{pair_number}") or {}
    
    return render_template('lesson_details.html', 
        lesson={
            'subject': lesson.get('subject', '—'),
            'group_name': group_name,
            'pair_number': pair_number,
            'time': lesson.get('time', ''),
            'date': date,
            'day_name': day_name,
            'room': lesson.get('room', '—'),
            'teacher': lesson.get('teacher', '—')
        },
        present_list=stats_data.get('presentList', []),
        absent_list=stats_data.get('absentList', []),
        stats={
            'total': stats_data.get('total', 0),
            'present': stats_data.get('present', 0),
            'absent': stats_data.get('absent', 0)
        }
    )

@app.route('/statistics/<group_name>')
def statistics_page(group_name):
    if group_name not in GROUPS:
        return render_template('404.html'), 404
    return render_template('statistics.html', group_name=group_name)

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

# API Прокси
@app.route('/attendance_stats/<group_name>/<date>/<pair_number>')
def attendance_stats_proxy(group_name, date, pair_number):
    try:
        response = requests.get(
            f"{API_BASE_URL}/attendance_stats/{group_name}/{date}/{pair_number}",
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('total', 0) > 0:
                return jsonify({
                    'has_data': True,
                    'total': data.get('total', 0),
                    'present': data.get('present', 0),
                    'absent': data.get('absent', 0),
                    'presentList': data.get('presentList', []),
                    'absentList': data.get('absentList', [])
                })
        return jsonify({'has_data': False, 'total': 0, 'present': 0, 'absent': 0})
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({'has_data': False, 'total': 0, 'present': 0, 'absent': 0})

@app.route('/attendance_trend/<group_name>')
def attendance_trend_proxy(group_name):
    period = request.args.get('period', 'week')
    year = request.args.get('year', '')
    month = request.args.get('month', '')
    semester = request.args.get('semester', '')
    
    url = f"{API_BASE_URL}/attendance_trend/{group_name}?period={period}"
    if year: url += f"&year={year}"
    if month: url += f"&month={month}"
    if semester: url += f"&semester={semester}"
    
    try:
        response = requests.get(url, timeout=10)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'dates': [], 'rates': []}), 500

@app.route('/student_stats/<group_name>')
def student_stats_proxy(group_name):
    try:
        response = requests.get(f"{API_BASE_URL}/student_stats/{group_name}", timeout=10)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify([]), 500

@app.route('/day_attendance/<group_name>/<date>')
def day_attendance_proxy(group_name, date):
    try:
        response = requests.get(f"{API_BASE_URL}/day_attendance/{group_name}/{date}", timeout=10)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)