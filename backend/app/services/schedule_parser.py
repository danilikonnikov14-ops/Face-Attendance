"""
Парсинг расписания с сайта
"""

import requests
from bs4 import BeautifulSoup
import re
from app.utils.logger import get_logger
from app.models.schedule import save_schedule

logger = get_logger(__name__)


def parse_schedule_from_site(group_name: str):
    """
    Парсит расписание с сайта для указанной группы
    
    Args:
        group_name: Название группы (например, "09.07.14п1")
    
    Returns:
        list: Список дней с расписанием
    """
    url = f"https://расписание.нхтк.рф/{group_name}.html"
    
    try:
        logger.info(f"🔄 Парсинг расписания для {group_name} с {url}")
        
        response = requests.get(url, timeout=15)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        days = []
        current_day = None
        current_date = None
        current_classes = []
        
        # Находим все строки с классом "занятие"
        for row in soup.find_all('tr', class_='занятие'):
            # Получаем день недели из предыдущей строки
            prev_row = row.find_previous_sibling('tr', class_='дата')
            if prev_row:
                day_div = prev_row.find('div', class_='день-недели')
                if day_div:
                    day_text = day_div.get_text(strip=True)
                    # Если день сменился, сохраняем предыдущий
                    if current_day != day_text:
                        if current_day and current_classes:
                            days.append({
                                'name': current_day,
                                'date': current_date or '',
                                'classes': current_classes.copy()
                            })
                        current_day = day_text
                        current_date = day_div.get('data-id', '')
                        current_classes = []
            
            # Получаем ячейки
            cells = row.find_all('td')
            if len(cells) >= 4:
                # НОМЕР ПАРЫ
                pair_num = row.get('data-pair-number', '')
                if pair_num:
                    pair_num = re.sub(r'[^0-9]', '', pair_num)
                    if len(pair_num) > 1:
                        pair_num = pair_num[0]
                else:
                    pair_text = cells[0].get_text(strip=True)
                    nums = re.findall(r'\d', pair_text)
                    pair_num = nums[0] if nums else '?'
                
                # ВРЕМЯ
                time_range = cells[1].get_text(strip=True)
                time_range = re.sub(r'\s+', ' ', time_range).strip()
                
                # ПРЕДМЕТ
                subject = cells[2].get_text(strip=True)
                
                # ПРЕПОДАВАТЕЛЬ
                teacher = cells[3].get_text(strip=True)
                
                # АУДИТОРИЯ
                room = cells[4].get_text(strip=True) if len(cells) >= 5 else ''
                
                if pair_num and subject and subject != '—':
                    current_classes.append({
                        'number': pair_num,
                        'time': time_range,
                        'subject': subject,
                        'teacher': teacher if teacher else '—',
                        'room': room if room else '—'
                    })
        
        # Добавляем последний день
        if current_day and current_classes:
            days.append({
                'name': current_day,
                'date': current_date or '',
                'classes': current_classes
            })
        
        total_classes = sum(len(d['classes']) for d in days)
        logger.info(f"✅ Расписание для {group_name}: {len(days)} дней, {total_classes} пар")
        
        return days
        
    except requests.exceptions.Timeout:
        logger.error(f"❌ Таймаут при парсинге {group_name}")
        return []
    except requests.exceptions.ConnectionError:
        logger.error(f"❌ Ошибка соединения при парсинге {group_name}")
        return []
    except Exception as e:
        logger.error(f"❌ Ошибка парсинга {group_name}: {e}")
        return []


def update_schedule_for_group(group_name):
    """Обновление расписания для одной группы"""
    days = parse_schedule_from_site(group_name)
    if days:
        return save_schedule(group_name, days)
    return 0


def update_all_schedules(groups):
    """Обновление расписания для всех групп"""
    logger.info("🔄 Запуск обновления расписания для всех групп...")
    
    total_saved = 0
    for group in groups:
        saved = update_schedule_for_group(group)
        total_saved += saved
    
    logger.info(f"✅ Обновление расписания завершено. Сохранено {total_saved} пар")
    return total_saved


def parse_schedule_mock(group_name):
    """
    Мок-функция для тестирования без реального сайта
    Возвращает тестовое расписание
    """
    return [
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
                },
                {
                    'number': '3',
                    'time': '12:00-13:30',
                    'subject': 'Информатика',
                    'teacher': 'Сидоров С.С.',
                    'room': '103'
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
                },
                {
                    'number': '2',
                    'time': '10:15-11:45',
                    'subject': 'Английский язык',
                    'teacher': 'Смирнова С.С.',
                    'room': '202'
                }
            ]
        }
    ]