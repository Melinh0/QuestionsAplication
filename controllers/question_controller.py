from flask import Blueprint, request, redirect, url_for, flash, jsonify
from models.topic_model import TopicModel
import os
import base64

question_bp = Blueprint('question', __name__)

@question_bp.route('/save', methods=['POST'])
def save():
    topic = request.form.get('topic')
    image_filename = request.form.get('image_filename')
    q_idx = request.form.get('q_idx')
    resposta = request.form.get('resposta')
    explicacao = request.form.get('explicacao')
    idx = request.form.get('idx')

    if not all([topic, image_filename, q_idx, idx]):
        if request.accept_mimetypes.accept_json:
            return jsonify({'error': 'Dados incompletos'}), 400
        return "Dados incompletos", 400

    try:
        q_idx = int(q_idx)
        idx = int(idx)
    except ValueError:
        if request.accept_mimetypes.accept_json:
            return jsonify({'error': 'Índice inválido'}), 400
        return "Índice inválido", 400

    updated = TopicModel.update_question(topic, image_filename, q_idx,
                                         {'resposta': resposta, 'explicacao': explicacao})
    if not updated:
        if request.accept_mimetypes.accept_json:
            return jsonify({'error': 'Questão não encontrada'}), 404
        return "Questão não encontrada", 404

    if request.accept_mimetypes.accept_json:
        return jsonify({'success': True})
    return redirect(url_for('topic.ver_topic', topic_name=topic, idx=idx, q=q_idx))

@question_bp.route('/topic/<topic_name>/add_question', methods=['POST'])
def add_question(topic_name):
    image_filename = request.form.get('image_filename')
    questao_num = request.form.get('questao_num', '').strip()
    tipo = request.form.get('tipo', '').strip()
    resposta = request.form.get('resposta', '').strip()
    explicacao = request.form.get('explicacao', '').strip()
    idx = request.form.get('idx', 0)

    if not image_filename or not questao_num:
        if request.accept_mimetypes.accept_json:
            return jsonify({'error': 'Número da questão é obrigatório.'}), 400
        flash('Número da questão é obrigatório.', 'error')
        return redirect(url_for('topic.ver_topic', topic_name=topic_name, idx=idx))

    questao_data = {
        "questao": questao_num,
        "tipo": tipo,
        "resposta": resposta,
        "explicacao": explicacao,
        "whiteboard_img": None
    }
    new_q_idx = TopicModel.add_question(topic_name, image_filename, questao_data)
    if request.accept_mimetypes.accept_json:
        return jsonify({'success': True, 'index': new_q_idx})
    flash('Questão adicionada com sucesso!', 'success')
    return redirect(url_for('topic.ver_topic', topic_name=topic_name, idx=idx, q=new_q_idx))

@question_bp.route('/topic/<topic_name>/delete_question', methods=['POST'])
def delete_question(topic_name):
    image_filename = request.form.get('image_filename')
    q_idx = request.form.get('q_idx')
    idx = request.form.get('idx', 0)

    if not image_filename or q_idx is None:
        if request.accept_mimetypes.accept_json:
            return jsonify({'error': 'Parâmetros insuficientes.'}), 400
        flash('Parâmetros insuficientes.', 'error')
        return redirect(url_for('topic.ver_topic', topic_name=topic_name, idx=idx))

    try:
        q_idx = int(q_idx)
        idx = int(idx)
    except ValueError:
        if request.accept_mimetypes.accept_json:
            return jsonify({'error': 'Índice inválido.'}), 400
        flash('Índice inválido.', 'error')
        return redirect(url_for('topic.ver_topic', topic_name=topic_name, idx=idx))

    deleted = TopicModel.delete_question(topic_name, image_filename, q_idx)
    if not deleted:
        if request.accept_mimetypes.accept_json:
            return jsonify({'error': 'Questão não encontrada.'}), 404
        flash('Questão não encontrada.', 'error')
        return redirect(url_for('topic.ver_topic', topic_name=topic_name, idx=idx))

    if request.accept_mimetypes.accept_json:
        return jsonify({'success': True})
    flash('Questão deletada com sucesso!', 'success')
    return redirect(url_for('topic.ver_topic', topic_name=topic_name, idx=idx, q=0))

@question_bp.route('/save_whiteboard', methods=['POST'])
def save_whiteboard():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400

    topic = data.get('topic')
    image_filename = data.get('image_filename')
    q_idx = data.get('q_idx')
    image_data = data.get('image_data')

    if not all([topic, image_filename, q_idx is not None, image_data]):
        return jsonify({'error': 'Parâmetros incompletos'}), 400

    try:
        q_idx = int(q_idx)
    except ValueError:
        return jsonify({'error': 'Índice inválido'}), 400

    header, encoded = image_data.split(',', 1)
    decoded = base64.b64decode(encoded)

    resolutions = TopicModel.get_resolutions(topic)
    found = False
    old_filename = None
    for item in resolutions:
        if item.get("imagem") == image_filename:
            questoes = item.get("questoes", [])
            if 0 <= q_idx < len(questoes):
                old_filename = questoes[q_idx].get('whiteboard_img')
                base_name = os.path.splitext(image_filename)[0]
                new_filename = f"whiteboard_{base_name}_q{q_idx}.png"
                questoes[q_idx]['whiteboard_img'] = new_filename
                found = True
            break

    if not found:
        return jsonify({'error': 'Questão não encontrada'}), 404

    whiteboard_folder = TopicModel.get_whiteboards_folder(topic)
    os.makedirs(whiteboard_folder, exist_ok=True)
    filepath = os.path.join(whiteboard_folder, new_filename)
    with open(filepath, 'wb') as f:
        f.write(decoded)

    if old_filename and old_filename != new_filename:
        old_path = os.path.join(whiteboard_folder, old_filename)
        if os.path.exists(old_path):
            os.remove(old_path)

    TopicModel.save_resolutions(topic, resolutions)
    return jsonify({'success': True, 'filename': new_filename})