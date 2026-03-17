import os

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    TOPICS_FOLDER = os.path.join(BASE_DIR, 'data', 'topics')
    IMAGES_TOPICS_FOLDER = os.path.join(BASE_DIR, 'static', 'images', 'topics')
    WHITEBOARDS_TOPICS_FOLDER = os.path.join(BASE_DIR, 'static', 'whiteboards', 'topics')
    QUESTIONS_UPLOAD_FOLDER = os.path.join(BASE_DIR, 'questions')
    SECRET_KEY = 'sua_chave_secreta_aqui'