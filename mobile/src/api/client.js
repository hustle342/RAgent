import axios from 'axios';

// Android emulator local IP'si 10.0.2.2'dir.
// Cihazda test ederken kendi IP'nizi yazmalısınız.
const API_BASE_URL = 'http://10.0.2.2:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const ragApi = {
  // Soru sorma
  askQuestion: (question, docIds = []) =>
    apiClient.post('/api/question', { question, document_ids: docIds }),

  // Doküman listesi çekme
  getDocuments: () => apiClient.get('/api/documents'),

  // Quiz oluşturma
  generateQuiz: (numQuestions = 5) =>
    apiClient.post('/api/quiz', { num_questions: numQuestions }),

  // Özet çıkarma
  getSummary: (docIds = []) =>
    apiClient.post('/api/summary', { document_ids: docIds }),
};

export default apiClient;
