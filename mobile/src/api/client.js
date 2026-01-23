import axios from 'axios';

// By default during local UI testing we mock backend calls so the app
// doesn't attempt network access from the emulator. Toggle OFFLINE_MOCK
// to false if you want real network behavior.
const OFFLINE_MOCK = true;

// Keep a production-capable client available if needed
const API_BASE_URL = 'http://192.168.1.164:8000';
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

let ragApi;
let defaultClient;

const mockDelay = (ms) => new Promise((res) => setTimeout(res, ms));

const mockResponses = {
  askQuestion: (question) => ({
    data: { answer: `Mock cevap: "${String(question).slice(0, 120)}"` },
  }),
  getDocuments: () => ({
    data: [
      { id: 'doc-1', title: 'Mock Doküman 1' },
      { id: 'doc-2', title: 'Mock Doküman 2' },
      { id: 'doc-3', title: 'Mock Doküman 3' },
    ],
  }),
  generateQuiz: (numQuestions = 5) => ({
    data: {
      quiz: Array.from({ length: numQuestions }).map((_, i) => ({
        id: `q-${i + 1}`,
        question: `Örnek soru ${i + 1}`,
        options: ['A', 'B', 'C', 'D'],
        correct_index: 0,
      })),
    },
  }),
  getSummary: (docIds = []) => ({ data: { summary: 'Bu bir mock özetidir.' } }),
};

if (OFFLINE_MOCK) {
  ragApi = {
    askQuestion: (question, docIds = []) => mockDelay(600).then(() => mockResponses.askQuestion(question)),
    getDocuments: () => mockDelay(200).then(() => mockResponses.getDocuments()),
    generateQuiz: (numQuestions = 5) => mockDelay(300).then(() => mockResponses.generateQuiz(numQuestions)),
    getSummary: (docIds = []) => mockDelay(300).then(() => mockResponses.getSummary(docIds)),
  };

  defaultClient = {
    get: (path) => {
      if (path.includes('/documents')) return Promise.resolve(mockResponses.getDocuments());
      return Promise.resolve({ data: null });
    },
    post: (path, body) => {
      if (path.includes('/question')) return Promise.resolve(mockResponses.askQuestion(body?.question || ''));
      if (path.includes('/quiz')) return Promise.resolve(mockResponses.generateQuiz(body?.num_questions || 5));
      if (path.includes('/summary')) return Promise.resolve(mockResponses.getSummary(body?.document_ids || []));
      return Promise.resolve({ data: null });
    },
  };
} else {
  ragApi = {
    askQuestion: (question, docIds = []) => apiClient.post('/api/question', { question, document_ids: docIds }),
    getDocuments: () => apiClient.get('/api/documents'),
    generateQuiz: (numQuestions = 5) => apiClient.post('/api/quiz', { num_questions: numQuestions }),
    getSummary: (docIds = []) => apiClient.post('/api/summary', { document_ids: docIds }),
  };

  defaultClient = apiClient;
}

export { ragApi };
export default defaultClient;
