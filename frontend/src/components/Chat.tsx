import React, { useEffect, useRef, useMemo } from 'react';
import { useChat } from '../hooks/useChat';
import { Message } from './Message';
import { ChatInput } from './ChatInput';

interface ChatProps {
  initialMessages?: Array<{ role: 'user' | 'assistant'; content: string }>;
  onMessagesChange?: (messages: Array<{ role: 'user' | 'assistant'; content: string }>) => void;
  onConversationUpdate?: () => void;
  onConversationSelect?: (conversationId: string, forceRerender?: boolean) => void;
  conversationId?: string | null;
}

export const Chat: React.FC<ChatProps> = ({ initialMessages, onMessagesChange, onConversationUpdate, onConversationSelect, conversationId }) => {
  const { messages, isLoading, error, sendMessage, clearChat } = useChat({
    initialMessages,
    onMessagesChange,
    onConversationUpdate,
    onConversationSelect,
    conversationId
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Memoize rendered messages for better performance
  const renderedMessages = useMemo(() => {
    console.log('Rendering messages:', messages.length, messages);
    return messages.map((message) => {
      console.log('Rendering message:', message.id, message.content, message.isStreaming);
      return (
        <Message 
          key={message.id} 
          message={message} 
        />
      );
    });
  }, [messages]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {renderedMessages}
        
        {error && (
          <div className="error">
            错误: {error}
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      <ChatInput onSendMessage={sendMessage} isLoading={isLoading} />
    </div>
  );
};