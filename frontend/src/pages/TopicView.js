import React, { useEffect, useState } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import {
  getTopic,
  updateQuestion,
  deleteQuestion,
  addQuestion,
  saveWhiteboard,
  renameTopic,
  getDownloadQuestionWhiteboardUrl,
  BACKEND_URL
} from '../services/api';
import Sidebar from '../components/Sidebar';
import ImageViewer from '../components/ImageViewer';
import QuestionEditor from '../components/QuestionEditor';
import Whiteboard from '../components/Whiteboard';

function TopicView() {
  const { topicName } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  const [images, setImages] = useState([]);
  const [resolutions, setResolutions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentIdx, setCurrentIdx] = useState(parseInt(searchParams.get('idx') || '0'));
  const [qIdx, setQIdx] = useState(parseInt(searchParams.get('q') || '0'));
  const [showAddModal, setShowAddModal] = useState(false);
  const [newQuestion, setNewQuestion] = useState({ questao_num: '', tipo: '', resposta: '', explicacao: '' });
  const [showRenameModal, setShowRenameModal] = useState(false);
  const [newTopicName, setNewTopicName] = useState(topicName);
  const [renameError, setRenameError] = useState('');
  const [activeTab, setActiveTab] = useState('texto');
  const [imageWidth, setImageWidth] = useState(50);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  useEffect(() => {
    getTopic(topicName)
      .then(res => {
        setImages(res.data.image_files || []);
        setResolutions(res.data.resolutions || []);
      })
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [topicName]);

  useEffect(() => {
    setCurrentIdx(parseInt(searchParams.get('idx') || '0'));
    setQIdx(parseInt(searchParams.get('q') || '0'));
  }, [searchParams]);

  const currentImage = images[currentIdx] || null;
  const currentRes = resolutions.find(r => r.imagem === currentImage) || { questoes: [] };
  const questions = currentRes.questoes || [];
  const currentQuestion = questions[qIdx] || null;

  // Constrói a URL usando a nova rota com CORS
  const whiteboardUrl = currentQuestion?.whiteboard_img
    ? `${BACKEND_URL}/whiteboard_image/${topicName}/${currentQuestion.whiteboard_img}`
    : null;

  const handlePrev = () => {
    if (currentIdx > 0) setSearchParams({ idx: currentIdx - 1, q: 0 });
  };
  const handleNext = () => {
    if (currentIdx < images.length - 1) setSearchParams({ idx: currentIdx + 1, q: 0 });
  };
  const handleQuestionChange = (newQIdx) => {
    setSearchParams({ idx: currentIdx, q: newQIdx });
  };

  const handleSaveQuestion = (updatedData) => {
    updateQuestion(topicName, currentImage, qIdx, updatedData)
      .then(() => {
        const newRes = resolutions.map(r => {
          if (r.imagem === currentImage) {
            const newQuestoes = [...r.questoes];
            newQuestoes[qIdx] = { ...newQuestoes[qIdx], ...updatedData };
            return { ...r, questoes: newQuestoes };
          }
          return r;
        });
        setResolutions(newRes);
      })
      .catch(err => console.error(err));
  };

  const handleDeleteQuestion = () => {
    if (!window.confirm('Tem certeza que deseja deletar esta questão?')) return;
    deleteQuestion(topicName, currentImage, qIdx, currentIdx)
      .then(() => {
        const newRes = resolutions.map(r => {
          if (r.imagem === currentImage) {
            const newQuestoes = r.questoes.filter((_, i) => i !== qIdx);
            return { ...r, questoes: newQuestoes };
          }
          return r;
        });
        setResolutions(newRes);
        setQIdx(0);
      })
      .catch(err => console.error(err));
  };

  const handleAddQuestion = () => {
    if (!newQuestion.questao_num) {
      alert('Número da questão é obrigatório.');
      return;
    }
    addQuestion(topicName, currentImage, { ...newQuestion, idx: currentIdx })
      .then(() => {
        return getTopic(topicName).then(res => {
          setResolutions(res.data.resolutions);
          const newRes = res.data.resolutions.find(r => r.imagem === currentImage);
          const newQIdx = newRes ? newRes.questoes.length - 1 : 0;
          setSearchParams({ idx: currentIdx, q: newQIdx });
        });
      })
      .catch(err => console.error(err))
      .finally(() => {
        setShowAddModal(false);
        setNewQuestion({ questao_num: '', tipo: '', resposta: '', explicacao: '' });
      });
  };

  const handleSaveWhiteboard = (imageData) => {
    saveWhiteboard(topicName, {
      topic: topicName,
      image_filename: currentImage,
      q_idx: qIdx,
      image_data: imageData
    })
      .then(res => {
        alert('Quadro salvo com sucesso!');
        const newFilename = res.data.filename;
        const newRes = resolutions.map(r => {
          if (r.imagem === currentImage) {
            const newQuestoes = [...r.questoes];
            newQuestoes[qIdx] = {
              ...newQuestoes[qIdx],
              whiteboard_img: newFilename
            };
            return { ...r, questoes: newQuestoes };
          }
          return r;
        });
        setResolutions(newRes);
      })
      .catch(err => alert('Erro ao salvar quadro.'));
  };

  const handleRename = (e) => {
    e.preventDefault();
    if (!newTopicName.trim()) {
      setRenameError('O nome não pode estar vazio.');
      return;
    }
    renameTopic(topicName, newTopicName)
      .then(res => {
        if (res.data.success) {
          navigate(`/topic/${res.data.new_name}`);
        } else {
          setRenameError(res.data.error || 'Erro ao renomear.');
        }
      })
      .catch(err => {
        setRenameError(err.response?.data?.error || 'Erro ao renomear.');
      });
  };

  const adjustColumns = (delta) => {
    setImageWidth(prev => Math.min(80, Math.max(20, prev + delta)));
  };

  const handleSliderChange = (e) => {
    setImageWidth(parseInt(e.target.value));
  };

  const toggleSidebar = () => {
    setSidebarCollapsed(prev => !prev);
  };

  if (loading) return <div className="container">Carregando...</div>;

  return (
    <div className="container">
      <Sidebar
        topicName={topicName}
        questions={questions}
        qIdx={qIdx}
        onQuestionChange={handleQuestionChange}
        collapsed={sidebarCollapsed}
      />
      <main className="content">
        <button className="toggle-sidebar-btn" id="toggleSidebarBtn" onClick={toggleSidebar}>☰</button>
        <div className="title-with-button">
          <h1>Resolução de Questões - {topicName}</h1>
          <button className="rename-btn" onClick={() => setShowRenameModal(true)} title="Renomear tópico">
            ✏️
          </button>
        </div>
        <hr />
        <div className="resize-controls">
          <button className="resize-btn" onClick={() => adjustColumns(-10)}>⇦ Imagem -</button>
          <span className="resize-value" id="imageWidthValue">{imageWidth}%</span>
          <input 
            type="range" 
            id="columnSlider" 
            className="resize-slider" 
            min="20" 
            max="80" 
            value={imageWidth} 
            onChange={handleSliderChange} 
            step="1"
          />
          <span className="resize-value" id="resolutionWidthValue">{100 - imageWidth}%</span>
          <button className="resize-btn" onClick={() => adjustColumns(10)}>Resolução + ⇨</button>
        </div>
        <div className="two-columns" id="twoColumns">
          <div className="image-col" style={{ flex: `0 0 ${imageWidth}%`, minWidth: '200px' }}>
            <ImageViewer
              topicName={topicName}
              currentImage={currentImage}
              currentIdx={currentIdx}
              total={images.length}
              onPrev={handlePrev}
              onNext={handleNext}
              onAddQuestion={() => setShowAddModal(true)}
              onImageDeleted={() => {
                const newImages = images.filter((_, i) => i !== currentIdx);
                setImages(newImages);
                if (newImages.length === 0) {
                  navigate('/');
                } else {
                  const newIdx = Math.min(currentIdx, newImages.length - 1);
                  setSearchParams({ idx: newIdx, q: 0 });
                }
              }}
            />
          </div>
          <div className="resolution-col" style={{ flex: `0 0 ${100 - imageWidth}%`, minWidth: '300px' }}>
            <h2>Conteúdo da Resolução</h2>
            <div className="resolution-tabs">
              <button
                className={`tab-button ${activeTab === 'texto' ? 'active' : ''}`}
                onClick={() => setActiveTab('texto')}
              >
                Texto
              </button>
              <button
                className={`tab-button ${activeTab === 'whiteboard' ? 'active' : ''}`}
                onClick={() => setActiveTab('whiteboard')}
              >
                Quadro Branco
              </button>
            </div>
            <div className={`tab-content ${activeTab === 'texto' ? 'active' : ''}`} id="tab-texto">
              {currentQuestion ? (
                <QuestionEditor
                  question={currentQuestion}
                  onSave={handleSaveQuestion}
                  onDelete={handleDeleteQuestion}
                  topicName={topicName}
                  imageFilename={currentImage}
                  qIdx={qIdx}
                  currentIdx={currentIdx}
                />
              ) : (
                <div className="info-message">Nenhuma questão encontrada para esta imagem.</div>
              )}
            </div>
            <div className={`tab-content ${activeTab === 'whiteboard' ? 'active' : ''}`} id="tab-whiteboard">
              {currentQuestion ? (
                <>
                  {/* key dinâmica garante a recriação do componente ao mudar de imagem/questão */}
                  <Whiteboard
                    key={`${currentImage}-${qIdx}`}
                    initialImage={whiteboardUrl}
                    onSave={handleSaveWhiteboard}
                  />
                  {currentQuestion.whiteboard_img && (
                    <div style={{ marginTop: '10px', textAlign: 'center' }}>
                      <a 
                        href={getDownloadQuestionWhiteboardUrl(topicName, currentImage, qIdx, currentIdx)}
                        className="button"
                        style={{ display: 'inline-block' }}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        📥 Baixar quadro
                      </a>
                    </div>
                  )}
                </>
              ) : (
                <div className="info-message">Selecione uma questão para usar o quadro branco.</div>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Modal de adicionar questão */}
      {showAddModal && (
        <div className="modal" style={{ display: 'block' }}>
          <div className="modal-content">
            <span className="close" onClick={() => setShowAddModal(false)}>&times;</span>
            <h2>Adicionar Nova Questão</h2>
            <form onSubmit={(e) => { e.preventDefault(); handleAddQuestion(); }}>
              <input type="hidden" name="image_filename" value={currentImage} />
              <input type="hidden" name="idx" value={currentIdx} />
              <div className="form-group">
                <label htmlFor="questao_num">Número da Questão *</label>
                <input
                  type="text"
                  id="questao_num"
                  className="form-control"
                  value={newQuestion.questao_num}
                  onChange={(e) => setNewQuestion({ ...newQuestion, questao_num: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="tipo">Tipo (opcional)</label>
                <input
                  type="text"
                  id="tipo"
                  className="form-control"
                  placeholder="ex: objetiva, discursiva"
                  value={newQuestion.tipo}
                  onChange={(e) => setNewQuestion({ ...newQuestion, tipo: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label htmlFor="resposta">Resposta (opcional)</label>
                <input
                  type="text"
                  id="resposta"
                  className="form-control"
                  value={newQuestion.resposta}
                  onChange={(e) => setNewQuestion({ ...newQuestion, resposta: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label htmlFor="explicacao">Resolução (Markdown/LaTeX) (opcional)</label>
                <textarea
                  id="explicacao"
                  rows="6"
                  className="form-control"
                  value={newQuestion.explicacao}
                  onChange={(e) => setNewQuestion({ ...newQuestion, explicacao: e.target.value })}
                ></textarea>
              </div>
              <button type="submit" className="save-button">Salvar Questão</button>
            </form>
          </div>
        </div>
      )}

      {/* Modal de renomear tópico */}
      {showRenameModal && (
        <div className="modal" style={{ display: 'block' }}>
          <div className="modal-content">
            <span className="close" onClick={() => setShowRenameModal(false)}>&times;</span>
            <h2>Renomear Tópico</h2>
            <form onSubmit={handleRename}>
              <div className="form-group">
                <label htmlFor="new_name">Novo nome:</label>
                <input
                  type="text"
                  id="new_name"
                  className="form-control"
                  value={newTopicName}
                  onChange={(e) => setNewTopicName(e.target.value)}
                  required
                />
              </div>
              {renameError && <div className="flash-error">{renameError}</div>}
              <button type="submit" className="save-button">Renomear</button>
              <button type="button" className="button" onClick={() => setShowRenameModal(false)} style={{ backgroundColor: '#6c757d' }}>Cancelar</button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default TopicView;