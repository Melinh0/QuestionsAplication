from flask import Blueprint, jsonify, request, url_for  
from models.topic_model import TopicModel
import os

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/topics', methods=['GET'])
def get_topics():
    topics = TopicModel.list_topics()
    return jsonify(topics)

@api_bp.route('/topics/<topic_name>', methods=['GET'])
def get_topic(topic_name):
    images_folder = TopicModel.get_images_folder(topic_name)
    if not os.path.exists(images_folder):
        return jsonify({'error': 'Tópico não encontrado.'}), 404
    image_files = TopicModel.get_image_files(topic_name)
    resolutions = TopicModel.get_resolutions(topic_name)

    # Adiciona whiteboard_url para cada questão
    for item in resolutions:
        for questao in item.get('questoes', []):
            whiteboard_img = questao.get('whiteboard_img')
            if whiteboard_img:
                questao['whiteboard_url'] = url_for('static', filename=f'whiteboards/topics/{topic_name}/{whiteboard_img}', _external=False)
            else:
                questao['whiteboard_url'] = None

    return jsonify({
        'image_files': image_files,
        'resolutions': resolutions
    })

@api_bp.route('/topics', methods=['POST'])
def create_topic():
    nome = request.form.get('nome', '').strip()
    if not nome:
        return jsonify({'success': False, 'error': 'Nome do tópico é obrigatório.'}), 400
    safe_name = TopicModel.create_topic(nome)
    return jsonify({'success': True, 'topic': safe_name})