import fitz  # PyMuPDF
import os
import re

# Suprime avisos do MuPDF (opcional)
fitz.TOOLS.mupdf_warnings(False)

# --- CONFIGURAÇÕES ---
caminho_origem = r"C:\Users\yagom\OneDrive\Documentos\QuestionsAplication\questions"
pasta_destino = r"C:\Users\yagom\OneDrive\Documentos\QuestionsAplication\static\images"

if not os.path.exists(pasta_destino):
    os.makedirs(pasta_destino)

# Margens de segurança (em pontos) – usadas apenas para detectar a primeira página
MARGEM_SUPERIOR = 50
MARGEM_INFERIOR = 70
TEXTO_MINIMO = 15

# Palavras que indicam instrução (para evitar falsos positivos)
PALAVRAS_INSTRUCAO = [
    'verifique', 'confira', 'atente', 'para marcar', 'não escreva',
    'não amasse', 'será considerada', 'lembre-se', 'ao terminar',
    'nesta prova', 'você dispõe', 'leia cuidadosamente', 'antes de transcrever'
]

def extrair_texto_completo(bloco):
    """Extrai todo o texto de um bloco de texto."""
    texto = ""
    for linha in bloco['lines']:
        for span in linha['spans']:
            texto += span['text']
        texto += " "
    return texto.strip()

def is_questao_valida(texto, bbox, page_height):
    """
    Verifica se o bloco corresponde a um início de questão válido.
    Retorna (bool, num_formatado) ou (False, None).
    """
    match = re.match(r'^(\d{1,2})[\.\s]', texto)
    if not match:
        return False, None
    num = int(match.group(1))
    if not (1 <= num <= 60):
        return False, None
    y0 = bbox[1]
    if y0 < MARGEM_SUPERIOR or y0 > page_height - MARGEM_INFERIOR:
        return False, None
    resto = texto[match.end():].strip()
    if len(resto) < TEXTO_MINIMO:
        return False, None
    resto_lower = resto.lower()
    if any(p in resto_lower for p in PALAVRAS_INSTRUCAO):
        return False, None
    palavras = resto.split()
    if not any(len(p) >= 3 for p in palavras):
        return False, None
    return True, str(num).zfill(2)

def encontrar_primeira_pagina_questao(doc):
    """
    Retorna o índice da primeira página que contém uma questão (número 01).
    Se não encontrar, retorna 2 (padrão).
    """
    for num_pag in range(len(doc)):
        pagina = doc[num_pag]
        blocos = pagina.get_text("dict")["blocks"]
        page_height = pagina.rect.height
        for b in blocos:
            if b['type'] != 0:
                continue
            texto = extrair_texto_completo(b)
            valido, _ = is_questao_valida(texto, b["bbox"], page_height)
            if valido:
                return num_pag
    return 2  # fallback

def processar_provas():
    arquivos = [f for f in os.listdir(caminho_origem) if f.lower().endswith(".pdf")]

    if not arquivos:
        print("Nenhum PDF encontrado.")
        return

    for nome_arquivo in arquivos:
        print(f"\n--- Analisando: {nome_arquivo} ---")
        caminho_pdf = os.path.join(caminho_origem, nome_arquivo)

        try:
            doc = fitz.open(caminho_pdf)
        except Exception as e:
            print(f"Erro ao abrir {nome_arquivo}: {e}")
            continue

        total_paginas = len(doc)
        
        # Verifica se o documento tem mais de 2 páginas
        if total_paginas <= 2:
            print(f"Arquivo {nome_arquivo} ignorado por ter apenas {total_paginas} páginas.")
            doc.close()
            continue

        # AJUSTE AQUI:
        # Começa no índice 2 (3ª página) e vai até o final (total_paginas)
        inicio_ajustado = 2 

        print(f"Processando da página {inicio_ajustado + 1} até a última ({total_paginas}).")

        for num_pag in range(inicio_ajustado, total_paginas):
            pagina = doc[num_pag]
            
            # Gerar imagem da página inteira
            pix = pagina.get_pixmap(matrix=fitz.Matrix(2, 2))  # resolução 2x
            nome_limpo = "".join(x for x in nome_arquivo.replace(".pdf", "") if x.isalnum() or x in "._- ")
            
            # O nome do arquivo manterá o número real da página no PDF (ex: pag003)
            nome_foto = f"{nome_limpo}_pag{num_pag+1:03d}.png"
            caminho_final = os.path.join(pasta_destino, nome_foto)
            pix.save(caminho_final)
            print(f"  [OK] Página {num_pag+1} salva.")

        doc.close()

if __name__ == "__main__":
    processar_provas()