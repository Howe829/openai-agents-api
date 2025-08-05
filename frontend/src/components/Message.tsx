import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Message as MessageType } from '../types';

interface MessageProps {
  message: MessageType;
}

const MessageComponent: React.FC<MessageProps> = ({ message }) => {
  const { role, content, isStreaming } = message;
  
  // 添加详细调试日志
  console.log('Message组件渲染:', { 
    id: message.id, 
    role, 
    content: content.substring(0, 50) + (content.length > 50 ? '...' : ''), 
    contentLength: content.length,
    isStreaming,
    timestamp: new Date().toISOString()
  });

  return (
    <div className={`message ${role} ${isStreaming ? 'streaming' : ''}`}>
      <div className="message-content">
        {role === 'assistant' ? (
          <ReactMarkdown>{content || (isStreaming ? '' : '')}</ReactMarkdown>
        ) : (
          content || (isStreaming ? '' : '')
        )}
        {isStreaming && <span className="streaming-indicator"> ...</span>}
      </div>
    </div>
  );
};

export const Message = MessageComponent;