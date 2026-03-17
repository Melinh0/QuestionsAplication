#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot para enviar imagens de páginas de prova ao Gemini e obter respostas/explicações.
Aceita argumentos:
--images: pasta com imagens
--json: arquivo JSON de saída
--sqlite: arquivo SQLite (opcional)
--coords: arquivo JSON com coordenadas personalizadas (opcional)

Comportamento:
- Processa todas as imagens da pasta.
- Para cada imagem, extrai questões via Gemini e mescla com as já existentes no JSON.
- Questões já presentes (mesmo número) são mantidas (prioridade manual).
- Apenas questões novas são adicionadas.
- Se SQLite estiver ativo, a tabela é atualizada com a lista final de questões da imagem.
"""

import os
import sys
import json
import time
import re
import sqlite3
import argparse
from datetime import datetime
import pyautogui
import pyperclip
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ==================== CONFIGURAÇÕES PADRÃO ====================
DEFAULT_COORD = {
    "campo_prompt": (77, 1015),
    "botao_anexar": (56, 1083),
    "botao_enviar_arquivos": (156, 850),
    "botao_abrir_dialogo": (848, 610),
    "enviar_mensagem": (898, 1079),
    "ver_mais_resposta": (899, 865),
    "copiar_resposta": (98, 721),
    "abrir_barra_lateral": (36, 156),
    "icone_chat": (340, 513),
    "excluir_chat": (416, 682),
    "confirmar_exclusao": (773, 719),
    "voltar_campo_prompt": (514, 1016),
}

WAIT_AFTER_SEND = 30
MAX_RETRIES = 1
DELAY_CLICK = 0.7
DELAY_TYPING = 0.5

PROMPT_TEMPLATE = """
Analise cuidadosamente a imagem fornecida e resolva todas as questões que aparecem nela.

Siga estas regras estritamente para evitar erros ou suposições:

REGRAS IMPORTANTES:
1. Leia o enunciado completo da questão antes de analisar.
2. Baseie sua resposta SOMENTE nas informações visíveis na imagem.
3. NÃO invente partes do enunciado ou alternativas que não estejam visíveis.
4. Se alguma parte essencial da questão estiver ilegível ou cortada, informe que não é possível determinar.
5. Identifique o tipo de questão:
   - **Múltipla escolha** (alternativas A, B, C, D, E)
   - **Certo/Errado** (C/E)
   - **Dissertativa** (resposta textual, numérica ou passo a passo)
6. Para questões objetivas, escolha apenas UMA alternativa.
7. Para questões dissertativas, forneça uma resposta completa e justificada, com cálculos ou argumentos se necessário.

Formato de resposta:

Para CADA questão, use o seguinte formato (exatamente como abaixo, com os cabeçalhos):

--- INÍCIO DA QUESTÃO ---
Número da questão: [número ou identificador]
Tipo: [objetiva|dissertativa]
Resposta: [para objetiva: letra; para dissertativa: texto da resposta]
Explicação: [explique detalhadamente o raciocínio, por que a alternativa está correta ou como chegou à resposta]
--- FIM DA QUESTÃO ---

Se houver mais de uma questão na imagem, repita o bloco para cada uma.

Exemplos:

--- INÍCIO DA QUESTÃO ---
Número da questão: 1
Tipo: objetiva
Resposta: B
Explicação: O enunciado pede a interpretação do sentido da metáfora "lâmina navalha" como representação de dor intensa. As demais alternativas interpretam o verso de forma literal ou apresentam temas que não aparecem no trecho.
--- FIM DA QUESTÃO ---

--- INÍCIO DA QUESTÃO ---
Número da questão: 2
Tipo: dissertativa
Resposta: O número que falta no vetor [3,0,1] é 2, pois o intervalo esperado é [0,3] e 2 não aparece.
Explicação: Utilizando a propriedade da soma dos números de 0 a n, podemos calcular o total esperado e subtrair a soma dos elementos presentes. Para n=3, a soma esperada é 0+1+2+3=6. A soma dos elementos é 3+0+1=4, logo o faltante é 2.
--- FIM DA QUESTÃO ---

Agora analise a imagem e responda.
"""

# ==================== FUNÇÕES AUXILIARES ====================
def carregar_coordenadas(arquivo_coords):
    """Carrega coordenadas de um arquivo JSON, mesclando com as padrão."""
    if arquivo_coords and os.path.exists(arquivo_coords):
        with open(arquivo_coords, 'r', encoding='utf-8') as f:
            user_coords = json.load(f)
        for k, v in user_coords.items():
            if isinstance(v, list):
                user_coords[k] = tuple(v)
        coords = DEFAULT_COORD.copy()
        coords.update(user_coords)
        return coords
    return DEFAULT_COORD

def clicar(coordenada, duplo=False):
    x, y = coordenada
    pyautogui.moveTo(x, y, duration=0.5)
    time.sleep(DELAY_CLICK)
    if duplo:
        pyautogui.doubleClick()
    else:
        pyautogui.click()
    time.sleep(DELAY_CLICK)

def escrever_texto(texto):
    pyautogui.typewrite(texto, interval=DELAY_TYPING)

def enviar_para_gemini(imagem_path, prompt, coords):
    try:
        clicar(coords["campo_prompt"])
        time.sleep(1)
        pyperclip.copy(prompt)
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)

        clicar(coords["botao_anexar"])
        time.sleep(2)
        clicar(coords["botao_enviar_arquivos"])
        time.sleep(2)
        pyperclip.copy(imagem_path)
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(1)
        clicar(coords["botao_abrir_dialogo"])
        time.sleep(3)

        clicar(coords["enviar_mensagem"])
        print("  ⏳ Aguardando resposta do Gemini...")
        time.sleep(WAIT_AFTER_SEND)

        try:
            clicar(coords["ver_mais_resposta"])
            time.sleep(2)
        except:
            pass

        clicar(coords["copiar_resposta"])
        time.sleep(1.5)
        resposta = pyperclip.paste()
        return resposta
    except Exception as e:
        print(f"  ❌ Erro ao interagir com Gemini: {e}")
        return None

def limpar_chat(coords):
    try:
        clicar(coords["abrir_barra_lateral"])
        time.sleep(1)
        clicar(coords["icone_chat"])
        time.sleep(1)
        clicar(coords["excluir_chat"])
        time.sleep(1)
        clicar(coords["confirmar_exclusao"])
        time.sleep(2)
        clicar(coords["voltar_campo_prompt"])
        time.sleep(1)
    except Exception as e:
        print(f"  ⚠️ Erro ao limpar chat: {e}")

def extrair_respostas(texto_resposta):
    resultados = []
    blocos = re.split(r'---\s*INÍCIO DA QUESTÃO\s*---', texto_resposta, flags=re.IGNORECASE)
    for bloco in blocos[1:]:
        match_fim = re.search(r'---\s*FIM DA QUESTÃO\s*---', bloco, flags=re.IGNORECASE)
        if match_fim:
            conteudo = bloco[:match_fim.start()].strip()
        else:
            conteudo = bloco.strip()
        numero = re.search(r'N[úu]mero da quest[ãa]o:\s*(.+)', conteudo, re.IGNORECASE)
        tipo = re.search(r'Tipo:\s*(.+)', conteudo, re.IGNORECASE)
        resposta = re.search(r'Resposta:\s*(.+)', conteudo, re.IGNORECASE)
        explicacao = re.search(r'Explica[çc][ãa]o:\s*(.+)', conteudo, re.DOTALL | re.IGNORECASE)
        if numero and tipo and resposta and explicacao:
            resultados.append({
                "questao": numero.group(1).strip(),
                "tipo": tipo.group(1).strip().lower(),
                "resposta": resposta.group(1).strip(),
                "explicacao": explicacao.group(1).strip()
            })
    return resultados

def inicializar_sqlite(sqlite_path):
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS respostas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            imagem TEXT NOT NULL,
            questao TEXT NOT NULL,
            resposta TEXT,
            explicacao TEXT,
            timestamp TEXT
        )
    ''')
    cursor.execute("PRAGMA table_info(respostas)")
    colunas = [coluna[1] for coluna in cursor.fetchall()]
    if 'tipo' not in colunas:
        cursor.execute("ALTER TABLE respostas ADD COLUMN tipo TEXT")
        print("✅ Coluna 'tipo' adicionada à tabela respostas.")
    conn.commit()
    conn.close()

def deletar_imagem_sqlite(sqlite_path, imagem):
    """Remove todas as entradas da imagem no SQLite."""
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM respostas WHERE imagem = ?", (imagem,))
    conn.commit()
    conn.close()

def salvar_sqlite(sqlite_path, imagem, questoes):
    """Insere as questões da imagem no SQLite (supõe que as antigas já foram deletadas)."""
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    for q in questoes:
        cursor.execute('''
            INSERT INTO respostas (imagem, questao, tipo, resposta, explicacao, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (imagem, q['questao'], q.get('tipo', ''), q['resposta'], q['explicacao'], timestamp))
    conn.commit()
    conn.close()

def merge_questoes_json(json_path, imagem, novas_questoes):
    """
    Faz o merge das novas questões com as existentes no JSON.
    Retorna a lista final de questões para a imagem.
    """
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            todas = json.load(f)
    else:
        todas = []

    for item in todas:
        if item.get("imagem") == imagem:
            existentes = {q['questao']: q for q in item['questoes']}
            for q in novas_questoes:
                if q['questao'] not in existentes:
                    item['questoes'].append(q)
            questoes_finais = item['questoes']
            break
    else:
        todas.append({
            "imagem": imagem,
            "data": datetime.now().isoformat(),
            "questoes": novas_questoes
        })
        questoes_finais = novas_questoes

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(todas, f, ensure_ascii=False, indent=2)

    return questoes_finais

# ==================== MAIN ====================
def main():
    parser = argparse.ArgumentParser(description='Processa imagens com Gemini')
    parser.add_argument('--images', required=True, help='Pasta com as imagens')
    parser.add_argument('--json', required=True, help='Arquivo JSON de saída')
    parser.add_argument('--sqlite', default=None, help='Arquivo SQLite de saída (opcional)')
    parser.add_argument('--coords', default=None, help='Arquivo JSON com coordenadas personalizadas (opcional)')
    args = parser.parse_args()

    PASTA_IMAGENS = args.images
    ARQUIVO_JSON = args.json
    ARQUIVO_SQLITE = args.sqlite
    ARQUIVO_COORDS = args.coords

    COORD = carregar_coordenadas(ARQUIVO_COORDS)

    if not os.path.exists(PASTA_IMAGENS):
        print(f"❌ Pasta não encontrada: {PASTA_IMAGENS}")
        sys.exit(1)

    imagens = [f for f in os.listdir(PASTA_IMAGENS) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    imagens.sort()
    print(f"📁 Encontradas {len(imagens)} imagens na pasta.")

    if os.path.exists(ARQUIVO_JSON):
        with open(ARQUIVO_JSON, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        processadas = {item['imagem'] for item in dados}
        print(f"✅ Imagens já presentes no JSON: {len(processadas)}")
    else:
        print("✅ Nenhum JSON existente. Será criado.")

    print(f"📝 Todas as {len(imagens)} imagens serão processadas (merge com existentes).")

    if ARQUIVO_SQLITE:
        inicializar_sqlite(ARQUIVO_SQLITE)

    print("\n🎯 Posicione o mouse sobre o campo do Gemini. Iniciando em 10 segundos...")
    for i in range(10, 0, -1):
        print(f"  {i}...")
        time.sleep(1)

    for idx, imagem in enumerate(imagens, 1):
        print(f"\n--- Processando imagem {idx}/{len(imagens)}: {imagem} ---")
        caminho_completo = os.path.join(PASTA_IMAGENS, imagem)

        sucesso = False
        for tentativa in range(1, MAX_RETRIES + 1):
            print(f"  Tentativa {tentativa}/{MAX_RETRIES}")
            limpar_chat(COORD)
            time.sleep(2)

            resposta = enviar_para_gemini(caminho_completo, PROMPT_TEMPLATE, COORD)

            if resposta:
                questoes = extrair_respostas(resposta)
                if questoes:
                    print(f"  ✅ {len(questoes)} questões extraídas.")
                    questoes_finais = merge_questoes_json(ARQUIVO_JSON, imagem, questoes)
                    if ARQUIVO_SQLITE:
                        deletar_imagem_sqlite(ARQUIVO_SQLITE, imagem)
                        salvar_sqlite(ARQUIVO_SQLITE, imagem, questoes_finais)
                    sucesso = True
                    break
                else:
                    debug_path = f"debug_{imagem}_tentativa{tentativa}.txt"
                    with open(debug_path, "w", encoding="utf-8") as f:
                        f.write(resposta)
                    print(f"  ⚠️ Extração falhou. Debug salvo: {debug_path}")
            else:
                print("  ⚠️ Resposta vazia ou erro.")

            if tentativa < MAX_RETRIES:
                print("  🔄 Nova tentativa em 5 segundos...")
                time.sleep(5)

        if not sucesso:
            print(f"  ❌ Falha ao processar {imagem}. Nenhuma questão adicionada.")

        if idx < len(imagens):
            print("  ⏳ Aguardando 10 segundos para próxima imagem...")
            time.sleep(10)

    print("\n✅ Processamento concluído!")

if __name__ == "__main__":
    main()