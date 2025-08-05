# OpenAI Agents API Demo

A demonstration project showcasing AI agent development using the `openai-agents-python` library. This project provides a complete chat application with both backend API and frontend interface, featuring intelligent agent-based conversations with context management and file handling capabilities.

## 🚀 Features

- **AI Agent Framework**: Built with `openai-agents-python` for intelligent conversation handling
- **Triage Agent**: Smart assistant that can handle various user requests and transfer to appropriate agents
- **Context Management**: Persistent conversation context with file ID support
- **Real-time Chat**: Streaming chat interface with real-time responses
- **Dark Mode**: Modern UI with light/dark theme toggle
- **Conversation Management**: Save, load, and manage multiple conversations
- **RESTful API**: FastAPI-based backend with comprehensive endpoints
- **Modern Frontend**: React + TypeScript frontend with responsive design

## 🏗️ Architecture

### Backend (FastAPI)
- **Agent System**: Modular agent architecture with triage capabilities
- **Database**: SQLModel-based data persistence
- **Streaming**: Real-time event streaming for chat responses
- **CORS Support**: Cross-origin resource sharing for frontend integration

### Frontend (React + TypeScript)
- **Modern UI**: Clean, responsive interface with dark mode support
- **Real-time Updates**: Live chat with streaming responses
- **Conversation History**: Persistent chat history management
- **Markdown Support**: Rich text rendering for agent responses

## 📋 Prerequisites

- Python 3.12+
- Node.js 18+
- npm or yarn

## 🛠️ Installation

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Howe829/openai-agents-api.git
   cd openai-agents-api
   ```

2. **Install Python dependencies**
   ```bash
   pip install -e .
   ```

3. **Environment Configuration**
   Create a `.env` file in the root directory:
   ```env
   DATABASE_URL=sqlite:///./chat.db
   DEBUG=true
   LLM_BASE_URL=your_llm_base_url
   LLM_API_KEY=your_api_key
   LLM_MODEL=your_model_name
   TIMEZONE=Asia/Shanghai
   ```

4. **Start the backend server**
   ```bash
   uvicorn server:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```

## 🚀 Usage

1. **Access the Application**
   - Frontend: http://localhost:3000 (or the port shown in terminal)
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

2. **Start Chatting**
   - Open the frontend in your browser
   - Start a new conversation
   - Chat with the AI agent
   - Use the context tools by providing file IDs when needed

3. **Agent Capabilities**
   - The triage agent can handle general questions
   - Use `get_context` to retrieve conversation context
   - Set file IDs using `set_current_file_id` for file-specific operations
   - Agent can transfer requests to specialized assistants when needed

## 📁 Project Structure

```
openai-agents-api/
├── _agents/                 # Agent implementations
│   ├── adapter.py          # Event stream adapter
│   ├── context.py          # Conversation context management
│   ├── events.py           # Event definitions
│   ├── models.py           # AI model configurations
│   └── triage.py           # Main triage agent
├── api/                    # FastAPI route handlers
│   ├── chat.py             # Chat endpoints
│   ├── conversation.py     # Conversation management
│   ├── message.py          # Message handling
│   └── file.py             # File operations
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── services/       # API service layer
│   │   └── types.ts        # TypeScript definitions
│   └── package.json
├── models/                 # Database models
├── schemas/                # Pydantic schemas
├── services/               # Business logic layer
├── tests/                  # Test suite
├── config.py               # Configuration management
├── database.py             # Database setup
└── server.py               # FastAPI application
```

## 🔧 API Endpoints

### Chat
- `GET /chat/agents` - List available agents
- `POST /chat/streaming` - Start streaming chat session

### Conversations
- `GET /conversation/list` - List conversations
- `POST /conversation/` - Create new conversation
- `DELETE /conversation/{id}` - Delete conversation

### Messages
- `GET /message/list/{conversation_id}` - Get conversation messages

## 🧪 Testing

Run the test suite:
```bash
pytest
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [openai-agents-python](https://github.com/openai/openai-agents-python)
- FastAPI for the robust backend framework
- React and TypeScript for the modern frontend
- SQLModel for elegant database operations

## 📞 Support

If you encounter any issues or have questions, please open an issue on GitHub.