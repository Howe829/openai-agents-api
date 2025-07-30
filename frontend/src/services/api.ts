import { ChatRequest, StreamEvent, Agent } from '../types';

const API_BASE_URL = 'http://localhost:8000/chat';
const CONVERSATION_API_BASE_URL = 'http://localhost:8000/conversation';
const MESSAGE_API_BASE_URL = 'http://localhost:8000/message';

export class ChatAPI {
  static async getAgents(): Promise<Agent[]> {
    const response = await fetch(`${API_BASE_URL}/agents`);
    if (!response.ok) {
      throw new Error('Failed to fetch agents');
    }
    return response.json();
  }

  static async *streamChat(request: ChatRequest): AsyncGenerator<StreamEvent, void, unknown> {
    const response = await fetch(`${API_BASE_URL}/streaming`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No response body');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.trim()) {
            try {
              const event: StreamEvent = JSON.parse(line);
              yield event;
            } catch (error) {
              console.warn('Failed to parse stream event:', line, error);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  // 对话相关API
  static async getConversations(page: number = 1, perPage: number = 20): Promise<any> {
    const response = await fetch(`${CONVERSATION_API_BASE_URL}/list?page=${page}&per_page=${perPage}&sort_field=updated_at&sort_order=desc`);
    if (!response.ok) {
      throw new Error('Failed to fetch conversations');
    }
    return response.json();
  }

  static async createConversation(): Promise<any> {
    const response = await fetch(`${CONVERSATION_API_BASE_URL}/new`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    if (!response.ok) {
      throw new Error('Failed to create conversation');
    }
    return response.json();
  }

  static async getConversation(conversationId: string): Promise<any> {
    const response = await fetch(`${CONVERSATION_API_BASE_URL}/${conversationId}`);
    if (!response.ok) {
      throw new Error('Failed to fetch conversation');
    }
    return response.json();
  }

  static async deleteConversation(conversationId: string): Promise<any> {
    const response = await fetch(`${CONVERSATION_API_BASE_URL}/${conversationId}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error('Failed to delete conversation');
    }
    return response.json();
  }

  // 消息相关API
  static async getMessages(conversationId: string): Promise<any> {
    const response = await fetch(`${MESSAGE_API_BASE_URL}/list?conversation_id=${conversationId}`);
    if (!response.ok) {
      throw new Error('Failed to fetch messages');
    }
    return response.json();
  }
}