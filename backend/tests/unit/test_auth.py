"""
Тесты аутентификации
"""

import pytest
from app.services.auth import hash_password, verify_password
from app.models.user import get_user_by_username, create_user


class TestAuth:
    """Тесты аутентификации"""
    
    def test_hash_password(self):
        """Тест хеширования пароля"""
        password = "test123"
        hashed = hash_password(password)
        
        assert hashed is not None
        assert len(hashed) == 64
        assert hashed != password
        assert hash_password(password) == hashed
    
    def test_verify_password(self):
        """Тест проверки пароля"""
        password = "test123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
        assert verify_password("wrong", hashed) is False
        assert verify_password("", hashed) is False
    
    def test_create_user(self, db):
        """Тест создания пользователя"""
        user = create_user(
            username="testuser",
            password="pass123",
            group_name="09.07.14п1",
            full_name="Test User"
        )
        
        assert user is not None
        assert user['username'] == "testuser"
        assert user['group_name'] == "09.07.14п1"
        
        # Проверка дубликата
        with pytest.raises(Exception):
            create_user("testuser", "pass123", "09.07.14п1", "Test User")
    
    def test_get_user(self, db, test_user):
        """Тест получения пользователя"""
        user = get_user_by_username(test_user['username'])
        assert user is not None
        assert user['username'] == test_user['username']
        
        user = get_user_by_username("nonexistent")
        assert user is None