from flask import Blueprint, send_file, send_from_directory, redirect, url_for, flash, request, jsonify
from models.topic_model import TopicModel
import os
import io
import zipfile
import sys
import subprocess
import logging

# Configura logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tenta importar PIL; se falhar, tenta instalar
try:
    from PIL import Image, ImageOps
except ImportError:
    logger.info("Pillow não encontrado. Tentando instalar...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image, ImageOps

download_bp = Blueprint('download', __name__)

def make_white_background(image_path):
    """
    Abre a imagem e garante que tenha fundo branco.
    Se a imagem tiver transparência, cola sobre branco.
    Se for RGB, apenas converte para RGB (não altera cores).
    Retorna um BytesIO com a imagem em PNG.
    """
    try:
        img = Image.open(image_path)
        logger.info(f"Imagem aberta: modo={img.mode}, formato={img.format}, tamanho={img.size}")

        # Converte para RGBA se necessário para preservar transparência
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Cria fundo branco do mesmo tamanho
        white_bg = Image.new('RGBA', img.size, (255, 255, 255, 255))
        
        # Cola a imagem sobre o fundo usando a própria imagem como máscara (se tiver canal alpha)
        white_bg.paste(img, (0, 0), img)
        
        # Converte para RGB (remove alfa) para garantir que não haja transparência no arquivo final
        result = white_bg.convert('RGB')
        
        output = io.BytesIO()
        result.save(output, format='PNG')
        output.seek(0)
        logger.info("Imagem processada com fundo branco.")
        return output
    except Exception as e:
        logger.error(f"Erro ao processar imagem {image_path}: {e}")
        # Em caso de erro, retorna o arquivo original
        with open(image_path, 'rb') as f:
            return io.BytesIO(f.read())

@download_bp.route('/topic/<topic_name>/download_image/<filename>')
def download_image(topic_name, filename):
    images_folder = TopicModel.get_images_folder(topic_name)
    filepath = os.path.join(images_folder, filename)
    if not os.path.exists(filepath):
        flash('Arquivo não encontrado.', 'error')
        return redirect(url_for('topic.ver_topic', topic_name=topic_name))
    return send_file(filepath, as_attachment=True, download_name=filename)

@download_bp.route('/topic/<topic_name>/download_all_images')
def download_all_images(topic_name):
    images_folder = TopicModel.get_images_folder(topic_name)
    if not os.path.exists(images_folder):
        flash('Pasta de imagens não encontrada.', 'error')
        return redirect(url_for('topic.ver_topic', topic_name=topic_name))
    image_files = [f for f in os.listdir(images_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    if not image_files:
        flash('Nenhuma imagem encontrada neste tópico.', 'error')
        return redirect(url_for('topic.ver_topic', topic_name=topic_name))
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for filename in image_files:
            filepath = os.path.join(images_folder, filename)
            zf.write(filepath, arcname=filename)
    memory_file.seek(0)
    return send_file(memory_file, download_name=f'{topic_name}_imagens.zip', as_attachment=True)

@download_bp.route('/topic/<topic_name>/download_text_resolutions')
def download_text_resolutions(topic_name):
    resolutions = TopicModel.get_resolutions(topic_name)
    if not resolutions:
        flash('Nenhuma resolução encontrada para este tópico.', 'error')
        return redirect(url_for('topic.ver_topic', topic_name=topic_name))
    
    lines = []
    lines.append(f"Resoluções do tópico: {topic_name}\n")
    lines.append("="*50 + "\n")
    for item in resolutions:
        image = item.get("imagem", "desconhecida")
        questoes = item.get("questoes", [])
        lines.append(f"Imagem: {image}\n")
        for q in questoes:
            lines.append(f"  Questão {q.get('questao', '?')}:\n")
            lines.append(f"    Tipo: {q.get('tipo', 'não especificado')}\n")
            lines.append(f"    Resposta: {q.get('resposta', '')}\n")
            lines.append(f"    Explicação:\n{q.get('explicacao', '')}\n\n")
        lines.append("-"*40 + "\n")
    
    content = "\n".join(lines)
    mem_file = io.BytesIO()
    mem_file.write(content.encode('utf-8'))
    mem_file.seek(0)
    return send_file(mem_file, as_attachment=True, download_name=f"{topic_name}_resolucoes.txt", mimetype='text/plain')

@download_bp.route('/topic/<topic_name>/download_whiteboards')
def download_whiteboards(topic_name):
    whiteboards_folder = TopicModel.get_whiteboards_folder(topic_name)
    if not os.path.exists(whiteboards_folder):
        flash('Pasta de quadros brancos não encontrada.', 'error')
        return redirect(url_for('topic.ver_topic', topic_name=topic_name))
    
    image_files = [f for f in os.listdir(whiteboards_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    if not image_files:
        flash('Nenhuma imagem de quadro branco encontrada neste tópico.', 'error')
        return redirect(url_for('topic.ver_topic', topic_name=topic_name))
    
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for filename in image_files:
            filepath = os.path.join(whiteboards_folder, filename)
            zf.write(filepath, arcname=filename)
    memory_file.seek(0)
    return send_file(memory_file, download_name=f'{topic_name}_quadros_brancos.zip', as_attachment=True)

@download_bp.route('/topic/<topic_name>/download_question_text/<path:image_filename>/<int:q_idx>')
def download_question_text(topic_name, image_filename, q_idx):
    idx = request.args.get('idx', 0)
    resolutions = TopicModel.get_resolutions(topic_name)
    item = next((item for item in resolutions if item.get("imagem") == image_filename), None)
    if not item:
        flash('Imagem não encontrada.', 'error')
        return redirect(url_for('topic.ver_topic', topic_name=topic_name, idx=idx))
    questoes = item.get("questoes", [])
    if q_idx < 0 or q_idx >= len(questoes):
        flash('Índice de questão inválido.', 'error')
        return redirect(url_for('topic.ver_topic', topic_name=topic_name, idx=idx))
    
    q = questoes[q_idx]
    content = f"Questão: {q.get('questao', '?')}\n"
    content += f"Tipo: {q.get('tipo', 'não especificado')}\n"
    content += f"Resposta: {q.get('resposta', '')}\n"
    content += f"Explicação:\n{q.get('explicacao', '')}\n"
    
    mem_file = io.BytesIO()
    mem_file.write(content.encode('utf-8'))
    mem_file.seek(0)
    safe_name = f"{topic_name}_questao_{q.get('questao', q_idx)}.txt"
    return send_file(mem_file, as_attachment=True, download_name=safe_name, mimetype='text/plain')

@download_bp.route('/topic/<topic_name>/download_question_whiteboard/<path:image_filename>/<int:q_idx>')
def download_question_whiteboard(topic_name, image_filename, q_idx):
    idx = request.args.get('idx', 0)
    resolutions = TopicModel.get_resolutions(topic_name)
    item = next((item for item in resolutions if item.get("imagem") == image_filename), None)
    if not item:
        flash('Imagem não encontrada.', 'error')
        return redirect(url_for('topic.ver_topic', topic_name=topic_name, idx=idx))
    questoes = item.get("questoes", [])
    if q_idx < 0 or q_idx >= len(questoes):
        flash('Índice de questão inválido.', 'error')
        return redirect(url_for('topic.ver_topic', topic_name=topic_name, idx=idx))
    
    whiteboard_img = questoes[q_idx].get('whiteboard_img')
    if not whiteboard_img:
        flash('Esta questão não possui imagem de quadro branco.', 'error')
        return redirect(url_for('topic.ver_topic', topic_name=topic_name, idx=idx))
    
    whiteboard_folder = TopicModel.get_whiteboards_folder(topic_name)
    filepath = os.path.join(whiteboard_folder, whiteboard_img)
    if not os.path.exists(filepath):
        flash('Arquivo de quadro branco não encontrado no servidor.', 'error')
        return redirect(url_for('topic.ver_topic', topic_name=topic_name, idx=idx))
    
    try:
        img_data = make_white_background(filepath)
        return send_file(img_data, as_attachment=True, download_name=whiteboard_img, mimetype='image/png')
    except Exception as e:
        flash(f'Erro ao processar imagem: {str(e)}', 'error')
        return redirect(url_for('topic.ver_topic', topic_name=topic_name, idx=idx))

# ================= ROTA CORRIGIDA PARA SERVIR IMAGENS COM CORS =================
@download_bp.route('/whiteboard_image/<topic_name>/<filename>')
def serve_whiteboard_image(topic_name, filename):
    whiteboard_folder = TopicModel.get_whiteboards_folder(topic_name)
    logger.info(f"Tentando servir arquivo: {filename} da pasta {whiteboard_folder}")
    
    # Verifica se a pasta existe
    if not os.path.isdir(whiteboard_folder):
        logger.error(f"Pasta não encontrada: {whiteboard_folder}")
        return jsonify({'error': 'Pasta não encontrada'}), 404
    
    # Usa send_from_directory para segurança
    try:
        response = send_from_directory(whiteboard_folder, filename, as_attachment=False)
        # Adiciona cabeçalho CORS para permitir acesso do frontend React
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        return response
    except FileNotFoundError:
        logger.error(f"Arquivo não encontrado: {filename}")
        return jsonify({'error': 'Arquivo não encontrado'}), 404