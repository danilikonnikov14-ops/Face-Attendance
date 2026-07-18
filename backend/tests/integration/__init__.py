"""
Интеграционные тесты
"""

from tests.integration.test_api import TestAPI
from tests.integration.test_attendance import TestAttendance
from tests.integration.test_database import TestDatabase

__all__ = [
    'TestAPI',
    'TestAttendance',
    'TestDatabase'
]