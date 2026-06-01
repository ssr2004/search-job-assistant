import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// 对话接口
export const chatApi = {
  stream: (sessionId: string, message: string, domain?: string) =>
    fetch('/api/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, message, domain }),
    }),
  getSessions: () => api.get('/chat/sessions'),
  getMessages: (sessionId: string) => api.get(`/chat/sessions/${sessionId}/messages`),
}

// 知识库接口
export const knowledgeApi = {
  upload: (file: File, domain?: string) => {
    const formData = new FormData()
    formData.append('file', file)
    if (domain) formData.append('domain', domain)
    return api.post('/knowledge/documents', formData)
  },
  getDocuments: () => api.get('/knowledge/documents'),
  deleteDocument: (id: number) => api.delete(`/knowledge/documents/${id}`),
  getStats: () => api.get('/knowledge/stats'),
}

// 简历接口
export const resumeApi = {
  upload: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/resume/upload', formData)
  },
  list: () => api.get('/resume/list'),
  getDetail: (id: number) => api.get(`/resume/${id}`),
}

// JD 接口
export const jdApi = {
  create: (title: string, rawText: string) =>
    api.post('/jd/create', { title, raw_text: rawText }),
  list: () => api.get('/jd/list'),
  getDetail: (id: number) => api.get(`/jd/${id}`),
}

// 匹配接口
export const matchApi = {
  run: (resumeId: number, jdId: number) =>
    api.post('/match', { resume_id: resumeId, jd_id: jdId }),
  getResults: () => api.get('/match/results'),
}

// 评估接口
export const evalApi = {
  createExperiment: (name: string) =>
    api.post('/eval/experiments', { name }),
  runExperiment: (id: number) =>
    api.post(`/eval/experiments/${id}/run`),
  getExperiment: (id: number) =>
    api.get(`/eval/experiments/${id}`),
}

// 技能差距接口
export const gapApi = {
  analyze: (resumeId: number, jdId: number) =>
    api.post('/gap/analyze', { resume_id: resumeId, jd_id: jdId }),
}

export default api
