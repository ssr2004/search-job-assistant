// 对话相关类型
export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface ChatSession {
  session_id: string
  title?: string
  domain?: string
}

// 知识库相关类型
export interface Document {
  id: number
  filename: string
  file_type: string
  file_size: number
  chunk_count: number
  domain?: string
  status: string
  created_at: string
}

export interface KnowledgeStats {
  total_documents: number
  total_chunks: number
  domains: string[]
}

// 简历相关类型
export interface Resume {
  id: number
  filename: string
  created_at: string
}

export interface ResumeDetail extends Resume {
  raw_text: string
  parsed_content?: Record<string, unknown>
}

export interface JobDescription {
  id: number
  title: string
  created_at: string
}

export interface JDDetail extends JobDescription {
  raw_text: string
  parsed_content?: Record<string, unknown>
}

// 匹配相关类型
export interface MatchResult {
  id: number
  resume_id: number
  jd_id: number
  final_score: number
  hard_score: number
  skill_score: number
  exp_score: number
  project_score: number
  details: Record<string, unknown>
  created_at: string
}

// 评估相关类型
export interface EvalExperiment {
  id: number
  name: string
  status: string
  faithfulness?: number
  context_precision?: number
  context_recall?: number
  answer_relevancy?: number
  details?: Record<string, unknown>
  created_at: string
}

// 技能差距相关类型
export interface GapAnalysis {
  required_match_rate: number
  preferred_match_rate: number
  overall_match_rate: number
  matched_required: string[]
  missing_required: string[]
  matched_preferred: string[]
  missing_preferred: string[]
  recommendations: Array<Record<string, unknown>>
}
