import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { uploadPDF } from '../services/api';

function UploadPDF() {
  const { topicName } = useParams();
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!file) {
      setError('Selecione um arquivo.');
      return;
    }
    uploadPDF(topicName, file)
      .then(res => {
        if (res.data.success) {
          sessionStorage.setItem('ultimo_pdf', res.data.pdf_path);
          navigate(`/topic/${topicName}/upload_success`);
        } else {
          setError('Erro ao enviar PDF.');
        }
      })
      .catch(err => {
        if (err.response && err.response.data && err.response.data.error) {
          setError(err.response.data.error);
        } else {
          setError('Erro ao enviar PDF.');
        }
      });
  };

  return (
    <div className="container">
      <main className="content" style={{ maxWidth: '600px', margin: '0 auto' }}>
        <h1>📤 Upload de PDF para "{topicName}"</h1>
        <hr />
        {error && <div className="flash-error">{error}</div>}
        <form onSubmit={handleSubmit} encType="multipart/form-data" className="edit-form">
          <div className="form-group">
            <label htmlFor="pdf">Selecione o arquivo PDF:</label>
            <input
              type="file"
              id="pdf"
              name="pdf"
              accept=".pdf"
              className="form-control"
              required
              onChange={(e) => setFile(e.target.files[0])}
            />
          </div>
          <button type="submit" className="save-button">Enviar</button>
          <Link to={`/topic/${topicName}`} className="button" style={{ backgroundColor: '#6c757d' }}>Voltar</Link>
        </form>
      </main>
    </div>
  );
}

export default UploadPDF;