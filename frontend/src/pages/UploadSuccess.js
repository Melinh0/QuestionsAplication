import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { extractImages } from '../services/api';

function UploadSuccess() {
  const { topicName } = useParams();
  const pdfPath = sessionStorage.getItem('ultimo_pdf') || ''; // Idealmente viria do state da navegação

  const handleExtract = () => {
    extractImages(topicName, pdfPath)
      .then(() => alert('Imagens extraídas!'))
      .catch(err => alert('Erro ao extrair imagens.'));
  };

  return (
    <div className="container">
      <main className="content" style={{ maxWidth: '600px', margin: '0 auto' }}>
        <h1>✅ PDF enviado com sucesso!</h1>
        <hr />
        <p>Arquivo: <strong>{pdfPath}</strong></p>
        <p>Deseja extrair as imagens deste PDF agora?</p>
        <button onClick={handleExtract} className="save-button">📸 Extrair imagens</button>
        <Link to={`/topic/${topicName}`} className="button" style={{ backgroundColor: '#6c757d' }}>Ir para o tópico</Link>
      </main>
    </div>
  );
}

export default UploadSuccess;