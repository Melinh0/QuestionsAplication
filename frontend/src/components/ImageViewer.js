import React from 'react';
import { getDownloadImageUrl, deleteImage } from '../services/api';

function ImageViewer({ topicName, currentImage, currentIdx, total, onPrev, onNext, onAddQuestion, onImageDeleted }) {
  const handleDelete = async () => {
    if (!window.confirm('Tem certeza que deseja deletar esta imagem? Essa ação não pode ser desfeita.')) return;
    try {
      await deleteImage(topicName, currentImage);
      alert('Imagem deletada com sucesso!');
      onImageDeleted(); // callback para atualizar a lista no componente pai
    } catch (err) {
      alert('Erro ao deletar imagem.');
    }
  };

  return (
    <div className="image-col" id="imageCol">
      {currentImage ? (
        <>
          <div className="image-nav-controls">
            <button onClick={onPrev} className="nav-btn" disabled={currentIdx === 0}>⬅️ Anterior</button>
            <span className="image-counter">{currentIdx + 1} / {total}</span>
            <button onClick={onNext} className="nav-btn" disabled={currentIdx === total - 1}>Próximo ➡️</button>
          </div>
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
              ⬇️ Download
            </a>
            <button className="button" onClick={onAddQuestion}>
              ➕ Adicionar Questão
            </button>
            <button className="delete-button" onClick={handleDelete}>
              🗑️ Excluir Imagem
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