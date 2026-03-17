import React from 'react';
import { getDownloadImageUrl } from '../services/api';

function ImageViewer({ topicName, currentImage, onAddQuestion }) {
  return (
    <div className="image-col" id="imageCol">
      {currentImage ? (
        <>
          <img
            src={`/static/images/topics/${topicName}/${currentImage}`}
            alt="Questão"
            className="question-image"
          />
          <p className="caption">Arquivo atual: {currentImage}</p>
          <div className="image-actions">
            <a
              href={getDownloadImageUrl(topicName, currentImage)}
              className="button"
              target="_blank"
              rel="noopener noreferrer"
            >
              ⬇️ Download Imagem
            </a>
            <button className="button" onClick={onAddQuestion}>
              ➕ Adicionar Questão
            </button>
          </div>
        </>
      ) : (
        <p>Nenhuma imagem disponível neste tópico.</p>
      )}
    </div>
  );
}

export default ImageViewer;