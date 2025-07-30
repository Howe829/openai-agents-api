import { useState, useCallback, useRef, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { Message, ChatRequest } from '../types';
import { ChatAPI } from '../services/api';

interface UseChatOptions {
  initialMessages?: Array<{ role: 'user' | 'assistant'; content: string }>;
  onMessagesChange?: (messages: Array<{ role: 'user' | 'assistant'; content: string }>) => void;
  onConversationUpdate?: () => void;
  onConversationSelect?: (conversationId: string) => void;
  conversationId?: string | null;
}

export const useChat = (options: UseChatOptions = {}) => {
  const { initialMessages = [], onMessagesChange, onConversationUpdate, onConversationSelect, conversationId: externalConversationId } = options;
  
  const [messages, setMessages] = useState<Message[]>(() => {
    return initialMessages.map(msg => ({
      id: uuidv4(),
      role: msg.role,
      content: msg.content,
      timestamp: new Date(),
    }));
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // 监听initialMessages变化，更新messages状态
  useEffect(() => {
    const newMessages = initialMessages.map(msg => ({
      id: uuidv4(),
      role: msg.role,
      content: msg.content,
      timestamp: new Date(),
    }));
    setMessages(newMessages);
  }, [JSON.stringify(initialMessages)]);

  // 使用useEffect来处理消息变化回调，避免在渲染期间调用
  useEffect(() => {
    if (onMessagesChange && messages.length > 0) {
      const simpleMessages = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }));
      onMessagesChange(simpleMessages);
    }
  }, [messages, onMessagesChange]);

  const addMessage = useCallback((message: Omit<Message, 'id' | 'timestamp'>) => {
    const newMessage: Message = {
      ...message,
      id: uuidv4(),
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, newMessage]);
    return newMessage.id;
  }, []);

  const updateMessage = useCallback((id: string, updates: Partial<Message>) => {
    console.log('updateMessage called with:', { id, updates });
    setMessages(prev => {
      console.log('updateMessage - prev messages:', prev);
      const newMessages = prev.map(msg => 
        msg.id === id ? { ...msg, ...updates } : msg
      );
      console.log('updateMessage - new messages:', newMessages);
      console.log('updateMessage - reference changed:', prev !== newMessages);
      return newMessages;
    });
  }, []);

  const sendMessage = useCallback(async (content: string, fileId?: string) => {
    if (!content.trim() || isLoading) return;

    setError(null);
    setIsLoading(true);

    // Add user message
    const userMessageId = addMessage({
      role: 'user',
      content: content.trim(),
    });

    // Add assistant message placeholder
    const assistantMessageId = addMessage({
      role: 'assistant',
      content: '',
      isStreaming: true,
    });
    console.log('创建assistant消息，ID:', assistantMessageId);

    try {
      const request: ChatRequest = {
        message: content.trim(),
        conversation_id: externalConversationId || conversationId || undefined,
        file_id: fileId,
      };

      let assistantContent = '';
      let currentConversationId = conversationId;

      for await (const event of ChatAPI.streamChat(request)) {
        console.log('接收到事件:', event);
        if (event.type === 'conversation_id' && event.data) {
          currentConversationId = event.data;
          setConversationId(event.data);
        } else if (event.name === 'NewConversationEvent' && event.conversation_id) {
          // 处理新对话创建事件
          currentConversationId = event.conversation_id;
          setConversationId(event.conversation_id);
          // 刷新对话列表并选中新对话
          if (onConversationUpdate) {
            onConversationUpdate();
          }
          if (onConversationSelect) {
            onConversationSelect(event.conversation_id);
          }
        } else if (event.name === 'MessageDeltaEvent' && event.delta) {
            // 处理消息增量事件，流式显示消息内容
            console.log('收到MessageDeltaEvent:', event);
            assistantContent += event.delta;
            console.log('累积内容更新:', { delta: event.delta, totalContent: assistantContent });
            
            // 直接更新messages状态，确保增量内容立即显示
            setMessages(prev => 
              prev.map(msg => 
                msg.id === assistantMessageId 
                  ? { ...msg, content: assistantContent, isStreaming: true } 
                  : msg
              )
            );
        } else if (event.name === 'NewMessageEvent' && event.content) {
          console.log('收到NewMessageEvent:', event);
          // NewMessageEvent表示消息完成，停止streaming状态
          updateMessage(assistantMessageId, {
            content: assistantContent || event.content,
            isStreaming: false
          });          console.log('已调用updateMessage完成消息ID:', assistantMessageId);
        } else if (event.type === 'content' && event.data) {
          assistantContent += event.data;
          updateMessage(assistantMessageId, {
            content: assistantContent,
            isStreaming: true,
          });
        } else if (event.type === 'done') {
          updateMessage(assistantMessageId, {
            isStreaming: false,
          });
          // 消息发送完成后刷新对话列表
          if (onConversationUpdate) {
            onConversationUpdate();
          }
        } else if (event.type === 'error') {
          throw new Error(event.data || 'Unknown error occurred');
        }
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      updateMessage(assistantMessageId, {
        content: `Error: ${errorMessage}`,
        isStreaming: false,
      });
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, conversationId, addMessage, updateMessage]);

  const clearChat = useCallback(() => {
    setMessages([]);
    setConversationId(null);
    setError(null);
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  }, []);

  const stopGeneration = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setIsLoading(false);
  }, []);

  return {
    messages,
    isLoading,
    error,
    conversationId,
    sendMessage,
    clearChat,
    stopGeneration,
  };
};