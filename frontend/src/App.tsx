import React, { useState, useCallback, useEffect } from 'react';
import { Chat } from './components/Chat';
import Sidebar from './components/Sidebar';
import { ChatAPI } from './services/api';

interface Conversation {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
  messages?: Array<{
    role: 'user' | 'assistant';
    content: string;
  }>;
}

function App() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [chatKey, setChatKey] = useState(0); // 用于重置Chat组件
  const [loading, setLoading] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(() => {
    // 从localStorage读取主题设置，默认为false（浅色模式）
    const saved = localStorage.getItem('darkMode');
    return saved ? JSON.parse(saved) : false;
  });

  // 加载对话列表
  const loadConversations = useCallback(async () => {
    try {
      setLoading(true);
      const response = await ChatAPI.getConversations();
      setConversations(response.conversations);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  // 组件挂载时加载对话列表
  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  const handleNewChat = useCallback(async () => {
    try {
      const newConversation = await ChatAPI.createConversation();
      setActiveConversationId(newConversation.id);
      setChatKey(prev => prev + 1);
      // 重新加载对话列表
      loadConversations();
    } catch (error) {
      console.error('Failed to create conversation:', error);
      // 如果创建失败，仍然允许本地新建对话
      setActiveConversationId(null);
      setChatKey(prev => prev + 1);
    }
  }, [loadConversations]);

  const handleSelectConversation = useCallback(async (id: string, forceRerender: boolean = true) => {
    setActiveConversationId(id);
    
    // 只有在需要强制重新渲染时才更新chatKey（比如用户手动选择对话）
    // 自动创建对话时不重新渲染，避免丢失流式消息状态
    if (forceRerender) {
      setChatKey(prev => prev + 1);
    }
    
    // 加载选中conversation的messages
    try {
      const messages = await ChatAPI.getMessages(id);
      // 更新conversations状态，添加messages
      setConversations(prev => 
        prev.map(conv => 
          conv.id === id 
            ? { 
                ...conv, 
                messages: messages.map((msg: any) => ({
                  role: msg.role,
                  content: msg.content
                }))
              }
            : conv
        )
      );
    } catch (error) {
      console.error('Failed to load messages:', error);
    }
  }, []);

  const handleDeleteConversation = useCallback(async (id: string) => {
    try {
      await ChatAPI.deleteConversation(id);
      // 如果删除的是当前活跃对话，清空选择
      if (activeConversationId === id) {
        setActiveConversationId(null);
        setChatKey(prev => prev + 1);
      }
      // 重新加载对话列表
      loadConversations();
    } catch (error) {
      console.error('Failed to delete conversation:', error);
    }
  }, [activeConversationId, loadConversations]);

  const handleSaveConversation = useCallback((messages: Array<{ role: 'user' | 'assistant'; content: string }>) => {
    if (messages.length === 0) return;
    
    // 对于现有对话，我们只在本地保存消息，实际的保存逻辑应该在聊天组件中处理
    // 这里主要是为了保持界面状态的一致性
    if (activeConversationId) {
      setConversations(prev => 
        prev.map(conv => 
          conv.id === activeConversationId 
            ? { ...conv, messages, updated_at: new Date().toISOString() }
            : conv
        )
      );
    }
  }, [activeConversationId]);

  // 切换主题模式
  const toggleDarkMode = useCallback(() => {
    setIsDarkMode((prev: boolean) => {
      const newMode = !prev;
      localStorage.setItem('darkMode', JSON.stringify(newMode));
      return newMode;
    });
  }, []);

  // 应用主题到document
  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark-mode');
    } else {
      document.documentElement.classList.remove('dark-mode');
    }
  }, [isDarkMode]);

  const activeConversation = conversations.find(conv => conv.id === activeConversationId);

  return (
    <div className="app-container">
      <Sidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={handleSelectConversation}
        onNewChat={handleNewChat}
        onDeleteConversation={handleDeleteConversation}
        isDarkMode={isDarkMode}
        onToggleDarkMode={toggleDarkMode}
      />
      <Chat 
        key={chatKey}
        initialMessages={activeConversation?.messages || []}
        onMessagesChange={handleSaveConversation}
        onConversationUpdate={loadConversations}
        onConversationSelect={handleSelectConversation}
        conversationId={activeConversationId}
      />
    </div>
  );
}

export default App;