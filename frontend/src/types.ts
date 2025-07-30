export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
}

export interface ChatRequest {
  conversation_id?: string;
  file_id?: string;
  message: string;
}

export interface StreamEvent {
  type?: string;
  data?: any;
  name?: string;
  delta?: string;
  content?: string;
  think?: string;
  agent?: string;
  conversation_id?: string;
  tool_name?: string;
  tool_call_id?: string;
  args?: string;
  output?: string;
  call_id?: string;
  timestamp?: number;
}

export interface Agent {
  name: string;
  description: string;
  handoffs: string[];
  tools: string[];
  input_guardrails: string[];
}