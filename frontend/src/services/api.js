import axios from 'axios';

export const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: '',
  headers: { 'Accept': 'application/json' }
});

// Tópicos
export const getTopics = () => api.get('/api/topics');
export const getTopic = (topicName) => api.get(`/api/topics/${topicName}`);
export const createTopic = (name) => {
  const formData = new URLSearchParams();
  formData.append('nome', name);
  return api.post('/api/topics', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  });
};
export const renameTopic = (oldName, newName) => {
  const formData = new URLSearchParams();
  formData.append('new_name', newName);
  return api.post(`/topic/${oldName}/rename`, formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  });
};
export const deleteImage = (topicName, filename) => {
  return api.post(`/topic/${topicName}/delete_image/${encodeURIComponent(filename)}`);
};

// Questões
export const addQuestion = (topicName, imageFilename, data) => {
  const formData = new URLSearchParams();
  formData.append('image_filename', imageFilename);
  formData.append('questao_num', data.questao_num);
  formData.append('tipo', data.tipo || '');
  formData.append('resposta', data.resposta || '');
  formData.append('explicacao', data.explicacao || '');
  formData.append('idx', data.idx || 0);
  return api.post(`/topic/${topicName}/add_question`, formData);
};
export const updateQuestion = (topicName, imageFilename, qIdx, data) => {
  const formData = new URLSearchParams();
  formData.append('topic', topicName);
  formData.append('image_filename', imageFilename);
  formData.append('q_idx', qIdx);
  formData.append('resposta', data.resposta);
  formData.append('explicacao', data.explicacao);
  formData.append('idx', data.idx);
  return api.post('/save', formData);
};
export const deleteQuestion = (topicName, imageFilename, qIdx, idx) => {
  const formData = new URLSearchParams();
  formData.append('image_filename', imageFilename);
  formData.append('q_idx', qIdx);
  formData.append('idx', idx);
  return api.post(`/topic/${topicName}/delete_question`, formData);
};

// Whiteboard
export const saveWhiteboard = (topicName, data) => api.post('/save_whiteboard', data);

// Uploads
export const uploadPDF = (topicName, file) => {
  const formData = new FormData();
  formData.append('pdf', file);
  return api.post(`/topic/${topicName}/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};
export const uploadImages = (topicName, files) => {
  const formData = new FormData();
  files.forEach(file => formData.append('images', file));
  return api.post(`/topic/${topicName}/upload_images`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};
export const extractImages = (topicName, pdfPath) => {
  const formData = new URLSearchParams();
  formData.append('pdf_path', pdfPath);
  return api.post(`/topic/${topicName}/extrair`, formData);
};

// Gemini
export const processGemini = (topicName) => api.post(`/topic/${topicName}/processar_gemini`);
export const executeGemini = (topicName, coords) => api.post(`/topic/${topicName}/executar_gemini`, { coords });
export const getMousePosition = () => api.post('/get_mouse_position');

// Downloads (links diretos) – usando BACKEND_URL
export const getDownloadImageUrl = (topicName, filename) => 
  `${BACKEND_URL}/topic/${topicName}/download_image/${encodeURIComponent(filename)}`;

export const getDownloadAllImagesUrl = (topicName) => 
  `${BACKEND_URL}/topic/${topicName}/download_all_images`;

export const getDownloadTextResolutionsUrl = (topicName) => 
  `${BACKEND_URL}/topic/${topicName}/download_text_resolutions`;

export const getDownloadWhiteboardsUrl = (topicName) => 
  `${BACKEND_URL}/topic/${topicName}/download_whiteboards`;

export const getDownloadQuestionTextUrl = (topicName, imageFilename, qIdx, idx) =>
  `${BACKEND_URL}/topic/${topicName}/download_question_text/${encodeURIComponent(imageFilename)}/${qIdx}?idx=${idx}`;

export const getDownloadQuestionWhiteboardUrl = (topicName, imageFilename, qIdx, idx) =>
  `${BACKEND_URL}/topic/${topicName}/download_question_whiteboard/${encodeURIComponent(imageFilename)}/${qIdx}?idx=${idx}`;