"""
Тесты распознавания лиц
"""

import pytest
import torch
from PIL import Image
from app.services.face_recognition import process_face, recognize_face, load_recognition_model


class TestFaceRecognition:
    """Тесты распознавания лиц"""
    
    def test_process_face_no_model(self):
        """Тест обработки лица без модели"""
        img = Image.new('RGB', (160, 160))
        result = process_face(img)
        assert result is None
    
    def test_recognize_face_empty_db(self):
        """Тест распознавания с пустой базой"""
        embedding = torch.tensor([0.1] * 512)
        name, similarity = recognize_face(embedding)
        assert name == "Неизвестный"
        assert similarity == -1
    
    def test_recognize_face_with_mock(self, mocker, mock_face_database):
        """Тест распознавания с моком"""
        import torch
        mock_db = {
            'Иванов Иван': torch.tensor([0.1] * 512),
            'Петров Петр': torch.tensor([0.2] * 512)
        }
        mocker.patch('app.services.face_recognition.face_database', mock_db)
        
        embedding = torch.tensor([0.11] * 512)
        name, similarity = recognize_face(embedding, threshold=0.5)
        
        assert name in ["Иванов Иван", "Неизвестный"]
        assert similarity >= -1