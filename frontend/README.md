# OpenAI Agents Chat Frontend

这是一个基于 React + TypeScript 的流式聊天前端应用，用于与 OpenAI Agents API 进行交互。

## 功能特性

- 🚀 实时流式聊天体验
- 💬 支持多轮对话
- 🎨 现代化的用户界面
- 📱 响应式设计
- ⚡ 基于 Vite 的快速开发

## 技术栈

- **React 18** - 用户界面库
- **TypeScript** - 类型安全的 JavaScript
- **Vite** - 快速的构建工具
- **CSS3** - 样式设计

## 快速开始

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

应用将在 http://localhost:3000 启动

### 构建生产版本

```bash
npm run build
```

## API 接口

前端通过以下接口与后端通信：

- `GET /chat/agents` - 获取可用的 agents 列表
- `POST /chat/streaming` - 发送消息并接收流式响应

## 项目结构

```
src/
├── components/          # React 组件
│   ├── Chat.tsx        # 主聊天组件
│   ├── Message.tsx     # 消息组件
│   └── ChatInput.tsx   # 输入组件
├── hooks/              # 自定义 Hooks
│   └── useChat.ts      # 聊天逻辑 Hook
├── services/           # API 服务
│   └── api.ts          # API 调用封装
├── types.ts            # TypeScript 类型定义
├── App.tsx             # 根组件
├── main.tsx            # 应用入口
└── index.css           # 全局样式
```

## 使用说明

1. 确保后端 API 服务器在 http://localhost:8000 运行
2. 在输入框中输入您的消息
3. 点击发送按钮或按 Enter 键发送消息
4. 系统将实时显示 AI 的流式回复
5. 可以点击"清空对话"按钮重新开始对话

## 开发说明

- 前端使用代理配置将 `/chat` 路径代理到后端服务器
- 支持流式数据处理，实时显示 AI 回复
- 使用 TypeScript 确保类型安全
- 响应式设计，支持移动端访问