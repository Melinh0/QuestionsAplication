import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';

import TopicsList from './pages/TopicsList';
import TopicView from './pages/TopicView';
import NewTopic from './pages/NewTopic';
import UploadPDF from './pages/UploadPDF';
import UploadImages from './pages/UploadImages';
import UploadSuccess from './pages/UploadSuccess';
import GeminiInstructions from './pages/GeminiInstructions';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<TopicsList />} />
        <Route path="/topic/novo" element={<NewTopic />} />
        <Route path="/topic/:topicName" element={<TopicView />} />
        <Route path="/topic/:topicName/upload" element={<UploadPDF />} />
        <Route path="/topic/:topicName/upload_images" element={<UploadImages />} />
        <Route path="/topic/:topicName/upload_success" element={<UploadSuccess />} />
        <Route path="/topic/:topicName/processar_gemini" element={<GeminiInstructions />} />
      </Routes>
    </Router>
  );
}

export default App;