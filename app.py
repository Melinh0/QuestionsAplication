import os
from flask import Flask
from config import Config
from utils.markdown import markdown_to_html
from flask_cors import CORS

# Criar pastas necessárias (garantia)
os.makedirs(Config.TOPICS_FOLDER, exist_ok=True)
os.makedirs(Config.IMAGES_TOPICS_FOLDER, exist_ok=True)
os.makedirs(Config.WHITEBOARDS_TOPICS_FOLDER, exist_ok=True)
os.makedirs(Config.QUESTIONS_UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)
app.secret_key = Config.SECRET_KEY

# Disponibilizar função markdown nos templates (opcional)
app.jinja_env.globals['markdown_to_html'] = markdown_to_html

# Registrar blueprints
from controllers.topic_controller import topic_bp
from controllers.upload_controller import upload_bp
from controllers.question_controller import question_bp
from controllers.gemini_controller import gemini_bp
from controllers.download_controller import download_bp
from controllers.api_controller import api_bp

app.register_blueprint(topic_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(question_bp)
app.register_blueprint(gemini_bp)
app.register_blueprint(download_bp)
app.register_blueprint(api_bp)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)