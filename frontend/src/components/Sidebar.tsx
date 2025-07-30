import React from 'react';
import './Sidebar.css';

interface Conversation {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
}

interface SidebarProps {
  conversations: Conversation[];
  activeConversationId: string | null;
  onSelectConversation: (id: string) => void;
  onNewChat: () => void;
  onDeleteConversation: (id: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewChat,
  onDeleteConversation
}) => {
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2>ChatGPT</h2>
        <button className="new-chat-btn" onClick={onNewChat}>
          + 新对话
        </button>
      </div>
      
      <div className="conversation-list">
        {conversations.length === 0 ? (
          <div style={{ 
            textAlign: 'center', 
            color: '#6c757d', 
            padding: '2rem 1rem',
            fontSize: '0.9rem'
          }}>
            暂无对话历史
          </div>
        ) : (
          conversations.map((conversation) => (
            <div
              key={conversation.id}
              className={`conversation-item ${
                activeConversationId === conversation.id ? 'active' : ''
              }`}
            >
              <div 
                className="conversation-content"
                onClick={() => onSelectConversation(conversation.id)}
              >
                <div className="conversation-title">
                  {conversation.name}
                </div>
                <div className="conversation-time">
                  {new Date(conversation.updated_at).toLocaleString('zh-CN', {
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </div>
              </div>
              <button 
                className="delete-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteConversation(conversation.id);
                }}
                title="删除对话"
              >
                ×
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Sidebar;