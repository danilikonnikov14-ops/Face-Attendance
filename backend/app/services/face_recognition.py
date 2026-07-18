"""
Сервис распознавания лиц
"""

import torch
import os
from facenet_pytorch import InceptionResnetV1, MTCNN
from PIL import Image
from app.config import config
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Определение устройства
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
logger.info(f"🔧 Используется устройство: {device}")

# Глобальные переменные
mtcnn = None
recognition_model = None
face_database = {}


def load_recognition_model():
    """Загрузка модели распознавания лиц"""
    global mtcnn, recognition_model, face_database
    
    if not os.path.exists(config.MODEL_PATH):
        logger.warning(f"⚠️ Модель не найдена по пути: {config.MODEL_PATH}")
        logger.warning("⚠️ Распознавание лиц будет недоступно")
        return False
    
    try:
        logger.info("🔄 Загрузка модели MTCNN...")
        mtcnn = MTCNN(image_size=160, margin=0, min_face_size=20, device=device)
        
        logger.info("🔄 Загрузка модели InceptionResnetV1...")
        recognition_model = InceptionResnetV1(pretrained='vggface2').eval().to(device)
        
        logger.info(f"🔄 Загрузка весов из: {config.MODEL_PATH}")
        checkpoint = torch.load(config.MODEL_PATH, map_location=device, weights_only=False)
        
        if 'embeddings' in checkpoint:
            for name, emb in checkpoint['embeddings'].items():
                if isinstance(emb, list):
                    emb = torch.tensor(emb)
                if torch.is_tensor(emb):
                    face_database[name] = emb.to(device)
                else:
                    face_database[name] = torch.tensor(emb).to(device)
        
        logger.info(f"✅ Загружено {len(face_database)} лиц для распознавания")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки модели: {e}")
        return False


def process_face(face_img):
    """Обработка лица - извлечение эмбеддинга"""
    if mtcnn is None or recognition_model is None:
        return None
    
    try:
        face = mtcnn(face_img)
        if face is not None:
            face = face.unsqueeze(0).to(device)
            with torch.no_grad():
                embedding = recognition_model(face).squeeze()
            return embedding
    except Exception as e:
        logger.error(f"❌ Ошибка обработки лица: {e}")
    
    return None


def recognize_face(face_embedding, threshold=0.5):
    """Распознавание лица по эмбеддингу"""
    if not face_database:
        return "Неизвестный", -1
    
    best_match = "Неизвестный"
    best_sim = -1
    
    try:
        for name, db_emb in face_database.items():
            sim = torch.nn.functional.cosine_similarity(
                face_embedding.unsqueeze(0), 
                db_emb.unsqueeze(0)
            ).item()
            
            if sim > best_sim and sim > threshold:
                best_sim = sim
                best_match = name
        
        return best_match, best_sim
        
    except Exception as e:
        logger.error(f"❌ Ошибка распознавания лица: {e}")
        return "Неизвестный", -1


def detect_faces(image):
    """Обнаружение лиц на изображении"""
    if mtcnn is None:
        return None, None
    
    try:
        boxes, probs = mtcnn.detect(image)
        return boxes, probs
        
    except Exception as e:
        logger.error(f"❌ Ошибка обнаружения лиц: {e}")
        return None, None


def get_face_database_stats():
    """Получение статистики базы лиц"""
    return {
        'total_faces': len(face_database),
        'names': list(face_database.keys())
    }


def add_face_to_database(name, embedding):
    """Добавление лица в базу (для будущего использования)"""
    global face_database
    if torch.is_tensor(embedding):
        face_database[name] = embedding.to(device)
    else:
        face_database[name] = torch.tensor(embedding).to(device)
    logger.info(f"✅ Добавлено лицо: {name}")
    return True


def remove_face_from_database(name):
    """Удаление лица из базы (для будущего использования)"""
    global face_database
    if name in face_database:
        del face_database[name]
        logger.info(f"✅ Удалено лицо: {name}")
        return True
    return False


def save_face_database(filepath):
    """Сохранение базы лиц (для будущего использования)"""
    try:
        embeddings = {}
        for name, emb in face_database.items():
            if torch.is_tensor(emb):
                embeddings[name] = emb.cpu().tolist()
            else:
                embeddings[name] = emb
        
        torch.save({'embeddings': embeddings}, filepath)
        logger.info(f"✅ База лиц сохранена в {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения базы лиц: {e}")
        return False