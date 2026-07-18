"""
Тесты парсера расписания
"""

import pytest
from app.services.schedule_parser import parse_schedule_mock


class TestScheduleParser:
    """Тесты парсера расписания"""
    
    def test_parse_mock_schedule(self):
        """Тест мок-парсинга расписания"""
        result = parse_schedule_mock("09.07.14п1")
        
        assert len(result) > 0
        assert result[0]['name'] == 'Понедельник'
        assert len(result[0]['classes']) > 0
        assert result[0]['classes'][0]['subject'] == 'Математика'
        assert result[0]['classes'][0]['teacher'] == 'Иванов И.И.'