import os
import json
import re
import shutil
from flask import current_app

class TopicModel:
    @staticmethod
    def get_topics_folder():
        return current_app.config['TOPICS_FOLDER']

    @staticmethod
    def get_images_folder(topic_name):
        return os.path.join(current_app.config['IMAGES_TOPICS_FOLDER'], topic_name)

    @staticmethod
    def get_whiteboards_folder(topic_name):
        return os.path.join(current_app.config['WHITEBOARDS_TOPICS_FOLDER'], topic_name)

    @staticmethod
    def get_questions_folder(topic_name):
        return os.path.join(current_app.config['QUESTIONS_UPLOAD_FOLDER'], topic_name)

    @staticmethod
    def get_json_path(topic_name):
        return os.path.join(current_app.config['TOPICS_FOLDER'], topic_name + '.json')

    @staticmethod
    def list_topics():
        topics = []
        topics_folder = current_app.config['TOPICS_FOLDER']
        if os.path.exists(topics_folder):
            for f in os.listdir(topics_folder):
                if f.endswith('.json'):
                    topics.append(f[:-5])
        return topics

    @staticmethod
    def topic_exists(topic_name):
        json_path = TopicModel.get_json_path(topic_name)
        return os.path.exists(json_path)

    @staticmethod
    def create_topic(topic_name):
        safe_name = re.sub(r'[^\w\-_]', '_', topic_name)
        os.makedirs(TopicModel.get_images_folder(safe_name), exist_ok=True)
        os.makedirs(TopicModel.get_whiteboards_folder(safe_name), exist_ok=True)
        os.makedirs(TopicModel.get_questions_folder(safe_name), exist_ok=True)
        json_path = TopicModel.get_json_path(safe_name)
        if not os.path.exists(json_path):
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump([], f)
        return safe_name

    @staticmethod
    def get_image_files(topic_name):
        folder = TopicModel.get_images_folder(topic_name)
        if not os.path.exists(folder):
            return []
        files = [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        files.sort()
        return files

    @staticmethod
    def get_resolutions(topic_name):
        json_path = TopicModel.get_json_path(topic_name)
        if not os.path.exists(json_path):
            return []
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def save_resolutions(topic_name, resolutions):
        json_path = TopicModel.get_json_path(topic_name)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(resolutions, f, ensure_ascii=False, indent=2)

    @staticmethod
    def get_questions_for_image(topic_name, image_filename):
        resolutions = TopicModel.get_resolutions(topic_name)
        item = next((item for item in resolutions if item.get("imagem") == image_filename), None)
        return item.get("questoes", []) if item else []

    @staticmethod
    def add_question(topic_name, image_filename, questao_data):
        resolutions = TopicModel.get_resolutions(topic_name)
        item = next((item for item in resolutions if item.get("imagem") == image_filename), None)
        if not item:
            item = {"imagem": image_filename, "questoes": []}
            resolutions.append(item)
        item["questoes"].append(questao_data)
        TopicModel.save_resolutions(topic_name, resolutions)
        return len(item["questoes"]) - 1

    @staticmethod
    def update_question(topic_name, image_filename, q_idx, updated_data):
        resolutions = TopicModel.get_resolutions(topic_name)
        for item in resolutions:
            if item.get("imagem") == image_filename:
                if 0 <= q_idx < len(item["questoes"]):
                    item["questoes"][q_idx].update(updated_data)
                    TopicModel.save_resolutions(topic_name, resolutions)
                    return True
        return False

    @staticmethod
    def delete_question(topic_name, image_filename, q_idx):
        resolutions = TopicModel.get_resolutions(topic_name)
        for item in resolutions:
            if item.get("imagem") == image_filename:
                if 0 <= q_idx < len(item["questoes"]):
                    del item["questoes"][q_idx]
                    TopicModel.save_resolutions(topic_name, resolutions)
                    return True
        return False

    @staticmethod
    def sanitize_topic_name(name):
        """Remove caracteres inválidos para nomes de pasta/arquivo."""
        name = re.sub(r'[<>:"/\\|?*]', '', name)
        return name.strip()

    @staticmethod
    def rename_topic(old_safe, new_safe, new_display_name):
        """
        Renomeia um tópico: move pastas e renomeia o arquivo JSON.
        Retorna (success, message).
        """
        try:
            # Move pastas
            old_img = TopicModel.get_images_folder(old_safe)
            new_img = TopicModel.get_images_folder(new_safe)
            if os.path.exists(old_img):
                shutil.move(old_img, new_img)

            old_wb = TopicModel.get_whiteboards_folder(old_safe)
            new_wb = TopicModel.get_whiteboards_folder(new_safe)
            if os.path.exists(old_wb):
                shutil.move(old_wb, new_wb)

            old_q = TopicModel.get_questions_folder(old_safe)
            new_q = TopicModel.get_questions_folder(new_safe)
            if os.path.exists(old_q):
                shutil.move(old_q, new_q)

            # Renomeia arquivo JSON
            old_json = TopicModel.get_json_path(old_safe)
            new_json = TopicModel.get_json_path(new_safe)
            if os.path.exists(old_json):
                shutil.move(old_json, new_json)

            return True, "OK"
        except Exception as e:
            return False, str(e)