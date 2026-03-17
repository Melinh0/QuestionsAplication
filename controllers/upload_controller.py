from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from models.topic_model import TopicModel
from services.image_service import allowed_file, extract_images_from_pdf, save_uploaded_images
from werkzeug.utils import secure_filename
import os

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/topic/<topic_name>/upload', methods=['GET', 'POST'])
def upload_pdf(topic_name):
    if request.method == 'POST':
        if 'pdf' not in request.files:
            if request.accept_mimetypes.accept_json:
                return jsonify({'success': False, 'error': 'Nenhum arquivo enviado.'}), 400
            flash('Nenhum arquivo enviado.', 'error')
            return redirect(request.url)
        file = request.files['pdf']
        if file.filename == '':
            if request.accept_mimetypes.accept_json:
                return jsonify({'success': False, 'error': 'Nenhum arquivo selecionado.'}), 400
            flash('Nenhum arquivo selecionado.', 'error')
            return redirect(request.url)
        if file and allowed_file(file.filename, {'pdf'}) and file.filename.lower().endswith('.pdf'):
            filename = secure_filename(file.filename)
            questions_folder = os.path.join(current_app.config['QUESTIONS_UPLOAD_FOLDER'], topic_name)
            os.makedirs(questions_folder, exist_ok=True)
            pdf_path = os.path.join(questions_folder, filename)
            file.save(pdf_path)
            if request.accept_mimetypes.accept_json:
                return jsonify({'success': True, 'pdf_path': pdf_path})
            flash('PDF enviado com sucesso!', 'success')
            session['ultimo_pdf'] = pdf_path
            return render_template('upload_success.html', topic=topic_name, pdf_path=pdf_path)
        else:
            if request.accept_mimetypes.accept_json:
                return jsonify({'success': False, 'error': 'Tipo de arquivo não permitido. Envie PDF.'}), 400
            flash('Tipo de arquivo não permitido. Envie PDF.', 'error')
            return redirect(request.url)
    return render_template('upload_pdf.html', topic=topic_name)

@upload_bp.route('/topic/<topic_name>/upload_images', methods=['GET', 'POST'])
def upload_images(topic_name):
    if request.method == 'POST':
        if 'images' not in request.files:
            if request.accept_mimetypes.accept_json:
                return jsonify({'success': False, 'error': 'Nenhum arquivo enviado.'}), 400
            flash('Nenhum arquivo enviado.', 'error')
            return redirect(request.url)
        files = request.files.getlist('images')
        if not files or files[0].filename == '':
            if request.accept_mimetypes.accept_json:
                return jsonify({'success': False, 'error': 'Nenhum arquivo selecionado.'}), 400
            flash('Nenhum arquivo selecionado.', 'error')
            return redirect(request.url)
        
        destino = TopicModel.get_images_folder(topic_name)
        saved_count = save_uploaded_images(files, destino)
        if request.accept_mimetypes.accept_json:
            return jsonify({'success': True, 'count': saved_count})
        flash(f'{saved_count} imagem(ns) enviada(s) com sucesso!', 'success')
        return redirect(url_for('topic.ver_topic', topic_name=topic_name))
    
    return render_template('upload_images.html', topic=topic_name)

@upload_bp.route('/topic/<topic_name>/extrair', methods=['POST'])
def extrair_imagens(topic_name):
    pdf_path = request.form.get('pdf_path')
    if not pdf_path or not os.path.exists(pdf_path):
        if request.accept_mimetypes.accept_json:
            return jsonify({'success': False, 'error': 'Arquivo PDF não encontrado.'}), 400
        flash('Arquivo PDF não encontrado.', 'error')
        return redirect(url_for('topic.ver_topic', topic_name=topic_name))
    destino = TopicModel.get_images_folder(topic_name)
    try:
        imagens_geradas = extract_images_from_pdf(pdf_path, destino)
        if request.accept_mimetypes.accept_json:
            return jsonify({'success': True, 'count': len(imagens_geradas)})
        flash(f'{len(imagens_geradas)} imagens extraídas com sucesso!', 'success')
    except Exception as e:
        if request.accept_mimetypes.accept_json:
            return jsonify({'success': False, 'error': str(e)}), 500
        flash(f'Erro ao extrair imagens: {str(e)}', 'error')
    return redirect(url_for('topic.ver_topic', topic_name=topic_name))