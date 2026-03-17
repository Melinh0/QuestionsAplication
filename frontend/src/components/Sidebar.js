import React from 'react';
import { Link } from 'react-router-dom';
import {
  getDownloadAllImagesUrl,
  getDownloadTextResolutionsUrl,
  getDownloadWhiteboardsUrl
} from '../services/api';

function Sidebar({ topicName, currentImage, currentIdx, total, questions, qIdx, onPrev, onNext, onQuestionChange, collapsed }) {
  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`} id="sidebar">
      <h2>Navegação</h2>
      <p><Link to="/">⬅️ Todos os tópicos</Link></p>
      <p><strong>Página atual:</strong> {currentImage}</p>
      <div className="nav-buttons">
        <button onClick={onPrev} className="button" disabled={currentIdx === 0}>⬅️ Anterior</button>
        <button onClick={onNext} className="button" disabled={currentIdx === total - 1}>Próximo ➡️</button>
      </div>
      {questions.length > 0 ? (
        <div className="question-selector">
          <label htmlFor="questao-select">Selecione a questão:</label>
          <select
            id="questao-select"
            value={qIdx}
            onChange={(e) => onQuestionChange(parseInt(e.target.value))}
          >
            {questions.map((q, idx) => (
              <option key={idx} value={idx}>Questão {q.questao || 'S/N'}</option>
            ))}
          </select>
        </div>
      ) : (
        <p>Nenhuma questão cadastrada para esta imagem.</p>
      )}
      <div style={{ marginTop: '20px' }}>
        <Link to={`/topic/${topicName}/upload`} className="button" style={{ display: 'block', marginBottom: '5px' }}>📤 Upload PDF</Link>
        <Link to={`/topic/${topicName}/upload_images`} className="button" style={{ display: 'block', marginBottom: '5px' }}>🖼️ Upload Imagens</Link>
        <Link to={`/topic/${topicName}/processar_gemini`} className="button" style={{ display: 'block', marginBottom: '5px' }}>🤖 Processar com Gemini</Link>
        <a href={getDownloadAllImagesUrl(topicName)} className="button" style={{ display: 'block', marginBottom: '5px' }} target="_blank" rel="noopener noreferrer">📥 Download Todas Imagens</a>
        <a href={getDownloadTextResolutionsUrl(topicName)} className="button" style={{ display: 'block', marginBottom: '5px' }} target="_blank" rel="noopener noreferrer">📥 Baixar resoluções (texto)</a>
        <a href={getDownloadWhiteboardsUrl(topicName)} className="button" style={{ display: 'block', marginBottom: '5px' }} target="_blank" rel="noopener noreferrer">📥 Baixar quadros brancos (zip)</a>
      </div>
    </aside>
  );
}

export default Sidebar;