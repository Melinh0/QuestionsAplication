import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { createTopic } from '../services/api';

function NewTopic() {
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!name.trim()) {
      setError('Nome do tópico é obrigatório.');
      return;
    }
    createTopic(name)
      .then(res => {
        if (res.data.success) {
          navigate('/');
        } else {
          setError('Erro ao criar tópico.');
        }
      })
      .catch(err => {
        if (err.response && err.response.data && err.response.data.error) {
          setError(err.response.data.error);
        } else {
          setError('Erro ao criar tópico.');
        }
      });
  };

  return (
    <div className="container">
      <main className="content" style={{ maxWidth: '500px', margin: '0 auto' }}>
        <h1>➕ Criar Novo Tópico</h1>
        <hr />
        {error && <div className="flash-error">{error}</div>}
        <form onSubmit={handleSubmit} className="edit-form">
          <div className="form-group">
            <label htmlFor="nome">Nome do Tópico:</label>
            <input
              type="text"
              id="nome"
              className="form-control"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>
          <button type="submit" className="save-button">Criar</button>
          <Link to="/" className="button" style={{ backgroundColor: '#6c757d' }}>Cancelar</Link>
        </form>
      </main>
    </div>
  );
}

export default NewTopic;