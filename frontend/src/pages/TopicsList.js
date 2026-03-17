import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getTopics } from '../services/api';

function TopicsList() {
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getTopics()
      .then(res => {
        console.log('Status:', res.status);
        console.log('Headers:', res.headers);
        console.log('Data:', res.data);
        if (Array.isArray(res.data)) {
          setTopics(res.data);
        } else {
          setError('Resposta inválida do servidor. Não é um array.');
          console.error('Resposta não é um array:', res.data);
        }
      })
      .catch(err => {
        setError('Erro ao carregar tópicos.');
        console.error(err);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="container">Carregando...</div>;
  if (error) return <div className="container">Erro: {error}</div>;

  return (
    <div className="container">
      <main className="content" style={{ maxWidth: '800px', margin: '0 auto' }}>
        <h1>📚 Tópicos de Estudo</h1>
        <ul style={{ listStyle: 'none', padding: 0, marginBottom: '20px' }}>
        <li>
          <Link to="/topic/novo" className="button" style={{ display: 'block', textAlign: 'left' }}>
            ➕ Criar Novo Tópico
          </Link>
        </li>
      </ul>
        {topics.length > 0 ? (
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {topics.map(topic => (
              <li key={topic} style={{ marginBottom: '10px' }}>
                <Link to={`/topic/${topic}`} className="button" style={{ display: 'block', textAlign: 'left' }}>
                  📁 {topic}
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <p>Nenhum tópico criado ainda. Crie um para começar!</p>
        )}
      </main>
    </div>
  );
}

export default TopicsList;