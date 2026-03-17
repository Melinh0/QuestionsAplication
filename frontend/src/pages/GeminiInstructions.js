import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { processGemini, executeGemini, getMousePosition } from '../services/api';

function GeminiInstructions() {
  const { topicName } = useParams();
  const navigate = useNavigate();

  const [coords, setCoords] = useState({});
  const [panelVisible, setPanelVisible] = useState(false);
  const [countdown, setCountdown] = useState({});
  const [capturing, setCapturing] = useState(null);
  const [output, setOutput] = useState('Aguardando início...');
  const [processing, setProcessing] = useState(false);
  const eventSourceRef = useRef(null);

  const coordKeys = [
    'campo_prompt', 'botao_anexar', 'botao_enviar_arquivos', 'botao_abrir_dialogo',
    'enviar_mensagem', 'ver_mais_resposta', 'copiar_resposta', 'abrir_barra_lateral',
    'icone_chat', 'excluir_chat', 'confirmar_exclusao', 'voltar_campo_prompt'
  ];

  useEffect(() => {
    processGemini(topicName)
      .then(res => {
        setCoords(res.data.default_coords || {});
        setPanelVisible(true);
      })
      .catch(err => console.error(err));
  }, [topicName]);

  const startCapture = (key) => {
    setCapturing(key);
    let seconds = 3;
    const interval = setInterval(() => {
      setCountdown(prev => ({ ...prev, [key]: seconds }));
      seconds--;
      if (seconds < 0) {
        clearInterval(interval);
        setCountdown(prev => ({ ...prev, [key]: null }));
        getMousePosition()
          .then(res => {
            setCoords(prev => ({
              ...prev,
              [key]: [res.data.x, res.data.y]
            }));
          })
          .catch(err => alert('Erro ao capturar posição'))
          .finally(() => setCapturing(null));
      }
    }, 1000);
  };

  const handleStartProcessing = () => {
    setProcessing(true);
    setOutput(prev => prev + '\n✅ Processo iniciado. Conectando ao stream...\n');
    executeGemini(topicName, { coords })
      .then(res => {
        if (res.data.success) {
          const es = new EventSource(`/topic/${topicName}/stream`);
          eventSourceRef.current = es;
          es.onmessage = (e) => {
            setOutput(prev => prev + e.data + '\n');
            if (e.data.includes('✅ Processamento concluído')) {
              es.close();
              setTimeout(() => navigate(`/topic/${topicName}`), 3000);
            }
          };
          es.onerror = () => {
            setOutput(prev => prev + '\n❌ Erro na conexão com o servidor.\n');
            es.close();
            setProcessing(false);
          };
        } else {
          setOutput(prev => prev + `\n❌ Erro ao iniciar: ${res.data.error}\n`);
          setProcessing(false);
        }
      })
      .catch(err => {
        setOutput(prev => prev + `\n❌ Falha na requisição: ${err.message}\n`);
        setProcessing(false);
      });
  };

  // Texto das instruções em Markdown (permite LaTeX)
  const instructionsMarkdown = `
### 📋 Instruções importantes:

1. Abra o **Gemini (gemini.google.com)** no seu navegador e faça login.
2. Garanta que a janela do navegador esteja visível e com o foco (não minimizada).
3. O bot irá controlar o mouse e teclado. **Não mexa** durante a execução.
4. Antes de iniciar, configure as coordenadas dos botões no painel abaixo. Para cada campo, clique em "Capturar": você terá 3 segundos para mover o mouse sobre o elemento correspondente no Gemini; após esse tempo, a posição será capturada automaticamente.
5. O processo pode levar vários minutos dependendo da quantidade de imagens.
6. Após iniciar, acompanhe o log. Quando terminar, você será redirecionado de volta ao tópico.
  `;

  return (
    <div className="container">
      <main className="content" style={{ maxWidth: '900px', margin: '0 auto' }}>
        <h1>🤖 Processar com Gemini - {topicName}</h1>
        <hr />

        <div className="instrucoes markdown-content">
          <ReactMarkdown
            remarkPlugins={[remarkMath]}
            rehypePlugins={[rehypeKatex]}
          >
            {instructionsMarkdown}
          </ReactMarkdown>
        </div>

        <button className="toggle-coords" onClick={() => setPanelVisible(!panelVisible)}>
          ⚙️ Configurar coordenadas
        </button>

        {panelVisible && (
          <div className="coords-panel">
            <h3>Coordenadas dos botões (X, Y)</h3>
            <div className="coords-grid">
              {coordKeys.map(key => (
                <div key={key} className="coord-item">
                  <label>{key}:</label>
                  <div className="coord-inputs">
                    <input
                      type="number"
                      value={coords[key] ? coords[key][0] : 0}
                      onChange={(e) => setCoords(prev => ({
                        ...prev,
                        [key]: [parseInt(e.target.value) || 0, prev[key] ? prev[key][1] : 0]
                      }))}
                      step="1"
                      placeholder="X"
                    />
                    <input
                      type="number"
                      value={coords[key] ? coords[key][1] : 0}
                      onChange={(e) => setCoords(prev => ({
                        ...prev,
                        [key]: [prev[key] ? prev[key][0] : 0, parseInt(e.target.value) || 0]
                      }))}
                      step="1"
                      placeholder="Y"
                    />
                    <button
                      className="capture-btn"
                      onClick={() => startCapture(key)}
                      disabled={capturing === key}
                    >
                      {capturing === key ? '⏳' : '📸'} Capturar
                    </button>
                    {countdown[key] > 0 && (
                      <span className="countdown">{countdown[key]}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
            <button className="save-coords-btn" onClick={() => setCoords(coords)}>Salvar coordenadas</button>
          </div>
        )}

        <div className="gemini-actions">
          <button
            id="startBtn"
            className="save-button"
            onClick={handleStartProcessing}
            disabled={processing}
          >
            {processing ? 'Processando...' : '▶️ Iniciar processamento'}
          </button>
          <a href={`/topic/${topicName}`} className="button" style={{ backgroundColor: '#6c757d' }}>Cancelar</a>
        </div>

        <div id="output" style={{ background: '#1e1e1e', color: '#0f0', padding: '1rem', borderRadius: '4px', fontFamily: 'monospace', whiteSpace: 'pre-wrap', maxHeight: '400px', overflowY: 'auto', marginTop: '1rem' }}>
          {output}
        </div>
      </main>
    </div>
  );
}

export default GeminiInstructions;