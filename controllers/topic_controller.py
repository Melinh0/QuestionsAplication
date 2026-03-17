from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models.topic_model import TopicModel
from utils.markdown import markdown_to_html
import os

topic_bp = Blueprint('topic', __name__)

@topic_bp.route('/')
def home():
    topics = TopicModel.list_topics()
    if request.accept_mimetypes.accept_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(topics)
    return render_template('topics.html', topicos=topics)

@topic_bp.route('/topic/novo', methods=['GET', 'POST'])
def novo_topic():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        if not nome:
            if request.accept_mimetypes.accept_json:
                return jsonify({'success': False, 'error': 'Nome do tópico é obrigatório.'}), 400
            flash('Nome do tópico é obrigatório.', 'error')
            return redirect(url_for('topic.novo_topic'))
        safe_name = TopicModel.create_topic(nome)
        if request.accept_mimetypes.accept_json:
            return jsonify({'success': True, 'topic': safe_name})
        flash(f'Tópico "{nome}" criado com sucesso!', 'success')
        return redirect(url_for('topic.ver_topic', topic_name=safe_name))
    return render_template('novo_topic.html')

@topic_bp.route('/topic/<topic_name>')
def ver_topic(topic_name):
    images_folder = TopicModel.get_images_folder(topic_name)
    if not os.path.exists(images_folder):
        if request.accept_mimetypes.accept_json:
            return jsonify({'error': 'Tópico não encontrado.'}), 404
        flash('Tópico não encontrado.', 'error')
        return redirect(url_for('topic.home'))

    image_files = TopicModel.get_image_files(topic_name)
    resolutions = TopicModel.get_resolutions(topic_name)

    if request.accept_mimetypes.accept_json:
        return jsonify({
            'image_files': image_files,
            'resolutions': resolutions
        })

    try:
        idx = int(request.args.get('idx', 0))
    except ValueError:
        idx = 0
    idx = max(0, min(idx, len(image_files)-1)) if image_files else 0
    current_img = image_files[idx] if image_files else None

    try:
        q_idx = int(request.args.get('q', 0))
    except ValueError:
        q_idx = 0

    res_data = None
    if current_img:
        res_data = next((item for item in resolutions if item.get("imagem") == current_img), None)

    questoes = res_data.get("questoes", []) if res_data else []

    if questoes:
        q_idx = max(0, min(q_idx, len(questoes)-1))
    else:
        q_idx = 0

    current_questao = None
    if questoes and q_idx < len(questoes):
        current_questao = questoes[q_idx].copy()
        current_questao['explicacao_html'] = markdown_to_html(current_questao.get('explicacao', ''))
        whiteboard_img = current_questao.get('whiteboard_img')
        if whiteboard_img:
            current_questao['whiteboard_url'] = url_for('static', filename=f'whiteboards/topics/{topic_name}/{whiteboard_img}')
        else:
            current_questao['whiteboard_url'] = None

    imagens_no_json = [item.get("imagem") for item in resolutions if isinstance(item, dict)]

    return render_template(
        'index.html',
        topic=topic_name,
        image_files=image_files,
        current_img=current_img,
        current_idx=idx,
        total=len(image_files),
        questoes=questoes,
        q_idx=q_idx,
        current_questao=current_questao,
        imagens_no_json=imagens_no_json,
    )

@topic_bp.route('/topic/<old_name>/rename', methods=['POST'])
def rename_topic(old_name):
    new_name = request.form.get('new_name', '').strip()
    if not new_name:
        if request.accept_mimetypes.accept_json:
            return jsonify({'success': False, 'error': 'O novo nome não pode estar vazio.'}), 400
        flash('O novo nome não pode estar vazio.', 'error')
        return redirect(url_for('topic.ver_topic', topic_name=old_name))

    safe_old = TopicModel.sanitize_topic_name(old_name)
    safe_new = TopicModel.sanitize_topic_name(new_name)

    if safe_old == safe_new:
        if request.accept_mimetypes.accept_json:
            return jsonify({'success': False, 'error': 'O novo nome é igual ao atual.'}), 400
        flash('O novo nome é igual ao atual.', 'info')
        return redirect(url_for('topic.ver_topic', topic_name=old_name))

    if TopicModel.topic_exists(safe_new):
        if request.accept_mimetypes.accept_json:
            return jsonify({'success': False, 'error': 'Já existe um tópico com este nome.'}), 400
        flash('Já existe um tópico com este nome.', 'error')
        return redirect(url_for('topic.ver_topic', topic_name=old_name))

    success, message = TopicModel.rename_topic(safe_old, safe_new, new_name)
    if success:
        if request.accept_mimetypes.accept_json:
            return jsonify({'success': True, 'new_name': safe_new})
        flash(f'Tópico renomeado para "{new_name}" com sucesso!', 'success')
        return redirect(url_for('topic.ver_topic', topic_name=safe_new))
    else:
        if request.accept_mimetypes.accept_json:
            return jsonify({'success': False, 'error': message}), 500
        flash(f'Erro ao renomear: {message}', 'error')
        return redirect(url_for('topic.ver_topic', topic_name=old_name))

@topic_bp.route('/topic/<topic_name>/delete_image/<path:filename>', methods=['POST'])
def delete_image(topic_name, filename):
    """
    Deleta uma imagem do tópico (do diretório de imagens e também das resoluções).
    """
    images_folder = TopicModel.get_images_folder(topic_name)
    filepath = os.path.join(images_folder, filename)
    
    if not os.path.exists(filepath):
        if request.accept_mimetypes.accept_json:
            return jsonify({'success': False, 'error': 'Arquivo não encontrado.'}), 404
        flash('Arquivo não encontrado.', 'error')
        return redirect(url_for('topic.ver_topic', topic_name=topic_name))

    try:
        os.remove(filepath)

        resolutions = TopicModel.get_resolutions(topic_name)
        resolutions = [item for item in resolutions if item.get("imagem") != filename]
        TopicModel.save_resolutions(topic_name, resolutions)

        whiteboard_folder = TopicModel.get_whiteboards_folder(topic_name)
        if os.path.isdir(whiteboard_folder):
            for item in os.listdir(whiteboard_folder):
                if filename in item:
                    whiteboard_path = os.path.join(whiteboard_folder, item)
                    try:
                        if os.path.isfile(whiteboard_path):
                            os.remove(whiteboard_path)
                    except Exception as e:
                        print(f"Erro ao remover whiteboard {whiteboard_path}: {e}")

        if request.accept_mimetypes.accept_json:
            return jsonify({'success': True})
        flash('Imagem deletada com sucesso!', 'success')

    except PermissionError:
        if request.accept_mimetypes.accept_json:
            return jsonify({'success': False, 'error': 'Permissão negada para deletar o arquivo.'}), 500
        flash('Permissão negada para deletar o arquivo.', 'error')
    except Exception as e:
        if request.accept_mimetypes.accept_json:
            return jsonify({'success': False, 'error': str(e)}), 500
        flash(f'Erro ao deletar imagem: {str(e)}', 'error')

    return redirect(url_for('topic.ver_topic', topic_name=topic_name))