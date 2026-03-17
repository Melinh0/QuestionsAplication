import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import { getDownloadQuestionTextUrl } from '../services/api';

function QuestionEditor({ question, onSave, onDelete, topicName, imageFilename, qIdx, currentIdx }) {
  const [resposta, setResposta] = useState(question.resposta || '');
  const [explicacao, setExplicacao] = useState(question.explicacao || '');
  const [preview, setPreview] = useState(false);

  // Sincroniza o estado local quando a questão muda
  useEffect(() => {
    setResposta(question.resposta || '');
    setExplicacao(question.explicacao || '');
  }, [question]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave({ resposta, explicacao, idx: currentIdx });
  };

  return (
    <form onSubmit={handleSubmit} className="edit-form">
      <input type="hidden" name="topic" value={topicName} />
      <input type="hidden" name="image_filename" value={imageFilename} />
      <input type="hidden" name="idx" value={currentIdx} />
      <input type="hidden" name="q_idx" value={qIdx} />
      <div className="resolucao-block">
        <h3>Questão {question.questao || 'S/N'}</h3>
        {question.tipo && <p><strong>Tipo:</strong> {question.tipo}</p>}

        <div className="form-group">
          <label htmlFor="resposta"><strong>Resposta:</strong></label>
          <input
            type="text"
            id="resposta"
            name="resposta"
            className="form-control"
            value={resposta}
            onChange={(e) => setResposta(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label htmlFor="explicacao"><strong>Resolução (Markdown e LaTeX permitidos):</strong></label>
          <textarea
            id="explicacao"
            name="explicacao"
            rows="10"
            className="form-control"
            value={explicacao}
            onChange={(e) => setExplicacao(e.target.value)}
          />
          <small>Use **negrito**, *itálico* e LaTeX ($...$ ou $$...$$).</small>
        </div>

        <div style={{ marginBottom: '1rem' }}>
          <button
            type="button"
            onClick={() => setPreview(!preview)}
            className="button"
            style={{ backgroundColor: '#6c757d', marginRight: '0.5rem' }}
          >
            {preview ? 'Editar' : 'Visualizar'}
          </button>
        </div>

        {preview && (
          <div className="preview-block">
            <h4>Pré-visualização da Resolução:</h4>
            <div className="latex-content">
              <ReactMarkdown
                remarkPlugins={[remarkMath]}
                rehypePlugins={[rehypeKatex]}
              >
                {explicacao}
              </ReactMarkdown>
            </div>
          </div>
        )}

        <div className="action-buttons" style={{ display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
          <button type="submit" className="save-button">💾 Salvar Alterações</button>
          <button type="button" onClick={onDelete} className="delete-button">🗑️ Deletar Questão</button>
          <a
            href={getDownloadQuestionTextUrl(topicName, imageFilename, qIdx, currentIdx)}
            className="button"
            style={{ backgroundColor: '#6c757d' }}
          >
            📥 Baixar resolução (texto)
          </a>
        </div>
      </div>
    </form>
  );
}

export default QuestionEditor;