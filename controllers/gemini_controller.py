from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, Response, current_app
from models.topic_model import TopicModel
import os
import sys
import subprocess
import threading
import queue
import json
import tempfile
import logging

logger = logging.getLogger(__name__)

gemini_bp = Blueprint('gemini', __name__)

processes = {}

@gemini_bp.route('/topic/<topic_name>/processar_gemini', methods=['POST'])
def processar_gemini(topic_name):
    images_folder = TopicModel.get_images_folder(topic_name)
    json_file = TopicModel.get_json_path(topic_name)
    sqlite_file = os.path.join(current_app.config['BASE_DIR'], 'data', 'respostas_imagens.sqlite')
    answer_script = os.path.join(current_app.config['BASE_DIR'], 'services', 'answer.py')
    if not os.path.exists(answer_script):
        if request.accept_mimetypes.accept_json:
            return jsonify({'error': 'Script answer.py não encontrado em services/.'}), 404
        flash('Script answer.py não encontrado em services/.', 'error')
        return redirect(url_for('topic.ver_topic', topic_name=topic_name))
    session['gemini_params'] = {
        'images': images_folder,
        'json': json_file,
        'sqlite': sqlite_file
    }

    default_coords = {
        "campo_prompt": [77, 1015],
        "botao_anexar": [56, 1083],
        "botao_enviar_arquivos": [156, 850],
        "botao_abrir_dialogo": [848, 610],
        "enviar_mensagem": [898, 1079],
        "ver_mais_resposta": [899, 865],
        "copiar_resposta": [98, 721],
        "abrir_barra_lateral": [36, 156],
        "icone_chat": [340, 513],
        "excluir_chat": [416, 682],
        "confirmar_exclusao": [773, 719],
        "voltar_campo_prompt": [514, 1016],
    }
    saved_coords = session.get('gemini_coords', default_coords)

    if request.accept_mimetypes.accept_json:
        return jsonify({'default_coords': saved_coords})
    return render_template('gemini_instrucoes.html', topic=topic_name, default_coords=saved_coords)

@gemini_bp.route('/topic/<topic_name>/executar_gemini', methods=['POST'])
def executar_gemini_ajax(topic_name):
    global processes
    if topic_name in processes and processes[topic_name]['process'].poll() is None:
        return jsonify({'success': False, 'error': 'Já existe um processo em execução para este tópico.'})

    data = request.get_json()
    coords = data.get('coords') if data else None

    images_folder = TopicModel.get_images_folder(topic_name)
    json_file = TopicModel.get_json_path(topic_name)
    sqlite_file = os.path.join(current_app.config['BASE_DIR'], 'data', 'respostas_imagens.sqlite')
    answer_script = os.path.join(current_app.config['BASE_DIR'], 'services', 'answer.py')

    cmd = [
        sys.executable, answer_script,
        '--images', images_folder,
        '--json', json_file,
        '--sqlite', sqlite_file
    ]

    if coords:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(coords, f, ensure_ascii=False, indent=2)
            coords_file = f.name
        cmd.extend(['--coords', coords_file])
        session['gemini_coords'] = coords

    output_queue = queue.Queue()
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=True,
        encoding='utf-8'
    )

    def reader_thread(proc, queue):
        for line in iter(proc.stdout.readline, ''):
            queue.put(line)
        proc.stdout.close()
        queue.put(None)

    thread = threading.Thread(target=reader_thread, args=(process, output_queue))
    thread.daemon = True
    thread.start()

    processes[topic_name] = {
        'process': process,
        'queue': output_queue,
        'thread': thread
    }

    return jsonify({'success': True, 'message': 'Processo iniciado.'})

@gemini_bp.route('/topic/<topic_name>/stream')
def stream_gemini(topic_name):
    global processes
    def generate():
        if topic_name not in processes:
            yield "data: ❌ Nenhum processo em execução.\n\n"
            return
        q = processes[topic_name]['queue']
        while True:
            line = q.get()
            if line is None:
                break
            yield f"data: {line.strip()}\n\n"
        processes.pop(topic_name, None)
        yield "data: ✅ Processamento concluído!\n\n"
    return Response(generate(), mimetype="text/event-stream")

@gemini_bp.route('/get_mouse_position', methods=['POST'])
def get_mouse_position():
    """Executa o script position.py e retorna a posição do mouse em JSON."""
    logger.info("Rota /get_mouse_position chamada")
    try:
        script_path = os.path.join(current_app.config['BASE_DIR'], 'services', 'position.py')
        if not os.path.exists(script_path):
            logger.error(f"Script position.py não encontrado em {script_path}")
            return jsonify({'error': 'Script position.py não encontrado'}), 500

        result = subprocess.run(
            [sys.executable, script_path, '--json'],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode != 0:
            logger.error(f"Erro ao executar position.py: {result.stderr}")
            return jsonify({'error': 'Erro ao capturar posição'}), 500

        output = result.stdout.strip()
        logger.info(f"Saída do position.py: {output}")
        data = json.loads(output)
        return jsonify(data)
    except subprocess.TimeoutExpired:
        logger.error("Timeout ao executar position.py")
        return jsonify({'error': 'Tempo esgotado ao capturar posição'}), 500
    except Exception as e:
        logger.error(f"Exceção: {e}")
        return jsonify({'error': str(e)}), 500