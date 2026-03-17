import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { uploadImages } from '../services/api';

function UploadImages() {
  const { topicName } = useParams();
  const navigate = useNavigate();
  const [files, setFiles] = useState([]);
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (files.length === 0) {
      setError('Selecione pelo menos uma imagem.');
      return;
    }
    uploadImages(topicName, files)
      .then(res => {
        if (res.data.success) {
          navigate(`/topic/${topicName}`);
        } else {
          setError('Erro ao enviar imagens.');
        }
      })
      .catch(err => {
        if (err.response && err.response.data && err.response.data.error) {
          setError(err.response.data.error);
        } else {
          setError('Erro ao enviar imagens.');
        }
      });
  };

  return (
    <div className="container">
      <aside className="sidebar">
        <h2>📌 Navegação</h2>
        <p><Link to="/">⬅️ Todos os tópicos</Link></p>
        <p><Link to={`/topic/${topicName}`}>⬅️ Voltar para o tópico</Link></p>
      </aside>
      <main className="content">
        <h1>🖼️ Upload de Imagens - {topicName}</h1>
        <hr />
        {error && <div className="flash-error">{error}</div>}
        <form onSubmit={handleSubmit} encType="multipart/form-data">
          <div className="form-group">
            <label htmlFor="images">Selecione as imagens (png, jpg, jpeg, gif, bmp):</label>
            <input
              type="file"
              name="images"
              id="images"
              multiple
              accept="image/*"
              required
              className="form-control"
              onChange={(e) => setFiles(Array.from(e.target.files))}
            />
          </div>
          <button type="submit" className="button">Enviar Imagens</button>
        </form>
      </main>
    </div>
  );
}

export default UploadImages;