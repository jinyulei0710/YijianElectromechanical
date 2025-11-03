import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import './App.css'
import ExamQuestions from './components/ExamQuestions'

// API 基础 URL
const API_BASE_URL = 'http://localhost:5001/api'

function App() {
  const [activeView, setActiveView] = useState('chat') // 'chat' 或 'exam'
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [stats, setStats] = useState(null)
  const [selectedSubject, setSelectedSubject] = useState('')
  const messagesEndRef = useRef(null)

  // 科目列表
  const subjects = [
    { id: '', name: '全部科目' },
    { id: '工程经济', name: '工程经济' },
    { id: '机电实务', name: '机电实务' },
    { id: '法律法规', name: '法律法规' },
    { id: '项目管理', name: '项目管理' }
  ]

  // 滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  // 加载统计信息
  useEffect(() => {
    loadStats()
  }, [])

  // 自动滚动
  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const loadStats = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/stats`)
      if (response.data.success) {
        setStats(response.data.data)
      }
    } catch (error) {
      console.error('加载统计信息失败:', error)
    }
  }

  const handleSend = async () => {
    if (!inputValue.trim()) return

    const userMessage = {
      role: 'user',
      content: inputValue,
      timestamp: new Date().toLocaleTimeString()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setLoading(true)

    try {
      const response = await axios.post(`${API_BASE_URL}/ask`, {
        question: inputValue,
        subject_filter: selectedSubject || null
      })

      if (response.data.success) {
        const aiMessage = {
          role: 'assistant',
          content: response.data.data.answer,
          timestamp: new Date().toLocaleTimeString()
        }
        setMessages(prev => [...prev, aiMessage])
      } else {
        throw new Error(response.data.error)
      }
    } catch (error) {
      const errorMessage = {
        role: 'error',
        content: `错误: ${error.response?.data?.error || error.message}`,
        timestamp: new Date().toLocaleTimeString()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="app">
      {/* 头部 */}
      <header className="header">
        <h1>🎓 一建机电备考 AI 助手</h1>
        <div className="nav-tabs">
          <button
            className={`nav-tab ${activeView === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveView('chat')}
          >
            💬 AI问答
          </button>
          <button
            className={`nav-tab ${activeView === 'exam' ? 'active' : ''}`}
            onClick={() => setActiveView('exam')}
          >
            📝 历年真题
          </button>
        </div>
        {stats && activeView === 'chat' && (
          <div className="stats">
            <span>📚 知识库: {stats.total} 条记录</span>
            <span>📖 工程经济: {stats.by_subject?.工程经济 || 0}</span>
            <span>⚡ 机电实务: {stats.by_subject?.机电实务 || 0}</span>
            <span>⚖️ 法律法规: {stats.by_subject?.法律法规 || 0}</span>
            <span>📋 项目管理: {stats.by_subject?.项目管理 || 0}</span>
          </div>
        )}
      </header>

      {/* 主体内容 */}
      {activeView === 'exam' ? (
        <ExamQuestions />
      ) : (
        <div className="main-content">
          {/* 侧边栏 */}
          <aside className="sidebar">
          <h3>科目筛选</h3>
          <div className="subject-list">
            {subjects.map(subject => (
              <button
                key={subject.id}
                className={`subject-btn ${selectedSubject === subject.id ? 'active' : ''}`}
                onClick={() => setSelectedSubject(subject.id)}
              >
                {subject.name}
              </button>
            ))}
          </div>

          <div className="tips">
            <h3>💡 使用提示</h3>
            <ul>
              <li>直接输入问题，AI 会基于教材内容回答</li>
              <li>可以选择科目进行筛选</li>
              <li>支持多轮对话</li>
              <li>回答会标注参考来源</li>
            </ul>
          </div>
        </aside>

        {/* 聊天区域 */}
        <div className="chat-container">
          <div className="messages">
            {messages.length === 0 ? (
              <div className="welcome">
                <h2>👋 欢迎使用一建机电备考 AI 助手</h2>
                <p>请输入您的问题，我会基于教材内容为您解答</p>
                <div className="example-questions">
                  <h3>示例问题：</h3>
                  <button onClick={() => setInputValue('什么是工程造价？')}>
                    什么是工程造价？
                  </button>
                  <button onClick={() => setInputValue('机电工程施工的主要流程是什么？')}>
                    机电工程施工的主要流程是什么？
                  </button>
                  <button onClick={() => setInputValue('建设工程招投标的法律规定有哪些？')}>
                    建设工程招投标的法律规定有哪些？
                  </button>
                </div>
              </div>
            ) : (
              messages.map((msg, index) => (
                <div key={index} className={`message ${msg.role}`}>
                  <div className="message-header">
                    <span className="role">
                      {msg.role === 'user' ? '🙋 你' : msg.role === 'assistant' ? '🤖 AI助手' : '❌ 错误'}
                    </span>
                    <span className="timestamp">{msg.timestamp}</span>
                  </div>
                  <div className="message-content">
                    {msg.content}
                  </div>
                </div>
              ))
            )}
            {loading && (
              <div className="message assistant loading">
                <div className="message-header">
                  <span className="role">🤖 AI助手</span>
                </div>
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                  正在思考中...
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* 输入区域 */}
          <div className="input-area">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="输入您的问题... (按 Enter 发送，Shift+Enter 换行)"
              disabled={loading}
              rows={3}
            />
            <button
              onClick={handleSend}
              disabled={loading || !inputValue.trim()}
              className="send-btn"
            >
              {loading ? '发送中...' : '发送 📤'}
            </button>
          </div>
        </div>
        </div>
      )}

      {/* 页脚 */}
      <footer className="footer">
        <p>💡 提示：AI 回答基于2025年一建教材内容 | 🔒 数据安全：所有对话仅在本地处理</p>
      </footer>
    </div>
  )
}

export default App

