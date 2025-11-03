import { useState, useEffect } from 'react'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'
import './ExamQuestions.css'

const API_BASE_URL = 'http://localhost:5001/api'

function ExamQuestions() {
  const [activeTab, setActiveTab] = useState('choice') // choice 或 case
  const [questions, setQuestions] = useState([])
  const [cases, setCases] = useState([])
  const [currentIndex, setCurrentIndex] = useState(0) // 当前题目索引
  const [loading, setLoading] = useState(false)
  const [stats, setStats] = useState(null)
  const [showAnswer, setShowAnswer] = useState(false) // 是否显示答案
  const [aiAnalysis, setAiAnalysis] = useState(null) // AI解析内容
  const [loadingAI, setLoadingAI] = useState(false) // AI解析加载状态
  const [filters, setFilters] = useState({
    subject: '机电实务',
    year: '',
    type: ''
  })
  const [totalCount, setTotalCount] = useState(0)

  // 科目列表
  const subjects = [
    { id: '工程经济', name: '工程经济' },
    { id: '机电实务', name: '机电实务' },
    { id: '法律法规', name: '法律法规' },
    { id: '项目管理', name: '项目管理' }
  ]

  // 题型列表
  const questionTypes = [
    { id: '', name: '全部题型' },
    { id: '单选题', name: '单选题' },
    { id: '多选题', name: '多选题' }
  ]

  // 年份列表（2007-2021）
  const years = ['', ...Array.from({ length: 15 }, (_, i) => 2021 - i)]

  // 加载统计信息
  useEffect(() => {
    loadStats()
  }, [])

  // 加载题目
  useEffect(() => {
    setCurrentIndex(0) // 重置索引
    setShowAnswer(false) // 隐藏答案
    setAiAnalysis(null) // 清除AI解析
    if (activeTab === 'choice') {
      loadQuestions()
    } else {
      loadCases()
    }
  }, [activeTab, filters])

  const loadStats = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/exam/stats`)
      if (response.data.success) {
        setStats(response.data.data)
      }
    } catch (error) {
      console.error('加载统计信息失败:', error)
    }
  }

  const loadQuestions = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams({
        page: 1,
        page_size: 1000 // 一次加载更多题目
      })

      if (filters.subject) params.append('subject', filters.subject)
      if (filters.year) params.append('year', filters.year)
      if (filters.type) params.append('type', filters.type)

      const response = await axios.get(`${API_BASE_URL}/exam/questions?${params}`)

      if (response.data.success) {
        const data = response.data.data
        setQuestions(data.questions)
        setTotalCount(data.total)
      }
    } catch (error) {
      console.error('加载题目失败:', error)
      setQuestions([])
    } finally {
      setLoading(false)
    }
  }

  const loadCases = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams({
        page: 1,
        page_size: 1000
      })

      if (filters.subject) params.append('subject', filters.subject)
      if (filters.year) params.append('year', filters.year)

      const response = await axios.get(`${API_BASE_URL}/exam/cases?${params}`)

      if (response.data.success) {
        const data = response.data.data
        setCases(data.cases)
        setTotalCount(data.total)
      }
    } catch (error) {
      console.error('加载案例题失败:', error)
      setCases([])
    } finally {
      setLoading(false)
    }
  }

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }))
    setCurrentIndex(0)
    setShowAnswer(false)
  }

  // 上一题
  const handlePrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1)
      setShowAnswer(false)
      setAiAnalysis(null)
    }
  }

  // 下一题
  const handleNext = () => {
    const maxIndex = activeTab === 'choice' ? questions.length - 1 : cases.length - 1
    if (currentIndex < maxIndex) {
      setCurrentIndex(currentIndex + 1)
      setShowAnswer(false)
      setAiAnalysis(null)
    }
  }

  // 切换答案显示
  const toggleAnswer = () => {
    setShowAnswer(!showAnswer)
  }

  // 获取AI解析
  const getAIAnalysis = async () => {
    if (aiAnalysis) {
      setAiAnalysis(null)
      return
    }

    setLoadingAI(true)
    try {
      const currentItem = activeTab === 'choice' ? currentQuestion : currentCase

      let requestData = {}

      if (activeTab === 'choice') {
        requestData = {
          question: currentItem.question,
          options: currentItem.options,
          answer: currentItem.answer,
          subject: currentItem.subject
        }
      } else {
        const allQuestions = currentItem.sub_questions
          .map((sq, idx) => `${idx + 1}. ${sq.question}`)
          .join('\n')

        requestData = {
          question: `${currentItem.background}\n\n问题：\n${allQuestions}`,
          subject: currentItem.subject
        }
      }

      const response = await axios.post(`${API_BASE_URL}/exam/ai-analysis`, requestData)

      if (response.data.success) {
        setAiAnalysis(response.data.data)
      } else {
        alert('AI解析失败: ' + response.data.error)
      }
    } catch (error) {
      console.error('获取AI解析失败:', error)
      alert('获取AI解析失败，请稍后重试')
    } finally {
      setLoadingAI(false)
    }
  }

  // 获取当前题目
  const currentQuestion = activeTab === 'choice' ? questions[currentIndex] : null
  const currentCase = activeTab === 'case' ? cases[currentIndex] : null
  
  // 确保索引在有效范围内
  useEffect(() => {
    if (activeTab === 'choice' && questions.length > 0 && currentIndex >= questions.length) {
      setCurrentIndex(0)
    } else if (activeTab === 'case' && cases.length > 0 && currentIndex >= cases.length) {
      setCurrentIndex(0)
    }
  }, [activeTab, questions, cases, currentIndex])

  return (
    <div className="exam-questions" style={{ width: '100%', height: '100vh', display: 'flex', flexDirection: 'column', background: '#f5f7fa', overflow: 'hidden' }}>
      <div className="exam-questions-inner" style={{ display: 'flex', flexDirection: 'column', height: '100%', width: '100%', maxWidth: '1200px', margin: '0 auto', padding: '0 20px', boxSizing: 'border-box' }}>
        {/* 顶部信息栏 */}
        <div className="top-bar">
        <div className="progress-info">
          {activeTab === 'choice' ? (
            <span>选择题：{currentIndex + 1} / {questions.length}</span>
          ) : (
            <span>案例题：{currentIndex + 1} / {cases.length}</span>
          )}
        </div>
        <div className="filter-compact">
          <select
            value={filters.subject}
            onChange={(e) => handleFilterChange('subject', e.target.value)}
          >
            {subjects.map(s => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
          <select
            value={filters.year}
            onChange={(e) => handleFilterChange('year', e.target.value)}
          >
            <option value="">全部年份</option>
            {years.filter(y => y).map(y => (
              <option key={y} value={y}>{y}年</option>
            ))}
          </select>
          {activeTab === 'choice' && (
            <select
              value={filters.type}
              onChange={(e) => handleFilterChange('type', e.target.value)}
            >
              {questionTypes.map(t => (
                <option key={t.id} value={t.id}>{t.name}</option>
              ))}
            </select>
          )}
        </div>
      </div>

      {/* 标签页 */}
      <div style={{ display: 'flex', gap: '10px', padding: '15px 20px', background: 'white', borderBottom: '2px solid #e0e0e0', flexShrink: 0 }}>
        <button
          style={{
            flex: 1,
            padding: '12px 20px',
            border: 'none',
            background: activeTab === 'choice' ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : 'white',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '16px',
            fontWeight: 500,
            color: activeTab === 'choice' ? 'white' : '#666',
            transition: 'all 0.3s',
            boxShadow: activeTab === 'choice' ? '0 4px 12px rgba(102, 126, 234, 0.4)' : '0 2px 4px rgba(0, 0, 0, 0.1)'
          }}
          onClick={() => {
            setActiveTab('choice')
            setCurrentIndex(0)
            setShowAnswer(false)
            setAiAnalysis(null)
          }}
        >
          📝 选择题
        </button>
        <button
          style={{
            flex: 1,
            padding: '12px 20px',
            border: 'none',
            background: activeTab === 'case' ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : 'white',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '16px',
            fontWeight: 500,
            color: activeTab === 'case' ? 'white' : '#666',
            transition: 'all 0.3s',
            boxShadow: activeTab === 'case' ? '0 4px 12px rgba(102, 126, 234, 0.4)' : '0 2px 4px rgba(0, 0, 0, 0.1)'
          }}
          onClick={() => {
            setActiveTab('case')
            setCurrentIndex(0)
            setShowAnswer(false)
            setAiAnalysis(null)
          }}
        >
          📋 案例题
        </button>
      </div>

      {/* 题目卡片 */}
      <div className="question-container">
        {loading ? (
          <div className="loading">⏳ 加载中...</div>
        ) : activeTab === 'choice' ? (
          // 选择题卡片
          currentQuestion ? (
            <div className="question-card-single">
              <div className="card-header">
                <span className="question-number">第 {currentQuestion.number} 题</span>
                <span className="question-meta">
                  {currentQuestion.year}年 · {currentQuestion.subject} · {currentQuestion.type}
                </span>
              </div>

              <div className="card-body">
                <div className="question-text">{currentQuestion.question}</div>

                {currentQuestion.options && Object.keys(currentQuestion.options).length > 0 && (
                  <div className="options-list">
                    {Object.entries(currentQuestion.options).map(([key, value]) => (
                      <div key={key} className="option-item">
                        <span className="option-label">{key}</span>
                        <span className="option-text">{value}</span>
                      </div>
                    ))}
                  </div>
                )}

                {showAnswer && (
                  <div className="answer-section">
                    {currentQuestion.answer && (
                      <div className="answer-box">
                        <div className="answer-label">✅ 答案</div>
                        <div className="answer-content">{currentQuestion.answer}</div>
                      </div>
                    )}
                    {currentQuestion.analysis && (
                      <div className="analysis-box">
                        <div className="analysis-label">💡 解析</div>
                        <div className="analysis-content">{currentQuestion.analysis}</div>
                      </div>
                    )}
                  </div>
                )}
              </div>

              <div className="card-footer">
                <button
                  className="btn-answer"
                  onClick={toggleAnswer}
                >
                  {showAnswer ? '隐藏答案' : '查看答案'}
                </button>
                <button
                  className="btn-ai-analysis"
                  onClick={getAIAnalysis}
                  disabled={loadingAI}
                >
                  {loadingAI ? '⏳ AI解析中...' : aiAnalysis ? '隐藏AI解析' : '🤖 AI智能解析'}
                </button>
              </div>

              {aiAnalysis && (
                <div className="ai-analysis-section">
                  <div className="ai-analysis-header">🤖 AI智能解析（结合教材）</div>
                  <div className="ai-analysis-content">
                    <ReactMarkdown>{aiAnalysis.analysis}</ReactMarkdown>
                  </div>
                  {aiAnalysis.sources && aiAnalysis.sources.length > 0 && (
                    <div className="ai-sources">
                      <div className="sources-title">📚 参考来源：</div>
                      {aiAnalysis.sources.map((source, idx) => (
                        <div key={idx} className="source-item">
                          <div className="source-subject">{source.subject}</div>
                          <div className="source-content">{source.content}</div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          ) : (
            <div className="no-data">😔 暂无题目</div>
          )
        ) : (
          // 案例题卡片
          currentCase ? (
            <div className="case-card-single">
              <div className="card-header">
                <span className="case-title">{currentCase.title}</span>
                <span className="case-meta">
                  {currentCase.year}年 · {currentCase.subject}
                  {currentCase.score && ` · ${currentCase.score}分`}
                </span>
              </div>

              <div className="card-body">
                <div className="background-section">
                  <div className="section-title">📖 背景资料</div>
                  <div className="background-text">{currentCase.background}</div>
                </div>

                <div className="subquestions-section">
                  <div className="section-title">❓ 问题</div>
                  {currentCase.sub_questions && currentCase.sub_questions.map((sq, idx) => (
                    <div key={idx} className="subquestion-item">
                      <div className="subquestion-number">{sq.sub_number}.</div>
                      <div className="subquestion-content">
                        <div className="subquestion-text">{sq.question}</div>

                        {showAnswer && (
                          <>
                            {sq.answer && (
                              <div className="subquestion-answer">
                                <span className="label">✅ 答案：</span>
                                <span>{sq.answer}</span>
                              </div>
                            )}
                            {sq.analysis && (
                              <div className="subquestion-analysis">
                                <span className="label">💡 解析：</span>
                                <span>{sq.analysis}</span>
                              </div>
                            )}
                          </>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="card-footer">
                <button
                  className="btn-answer"
                  onClick={toggleAnswer}
                >
                  {showAnswer ? '隐藏答案' : '查看答案'}
                </button>
                <button
                  className="btn-ai-analysis"
                  onClick={getAIAnalysis}
                  disabled={loadingAI}
                >
                  {loadingAI ? '⏳ AI解析中...' : aiAnalysis ? '隐藏AI解析' : '🤖 AI智能解析'}
                </button>
              </div>

              {aiAnalysis && (
                <div className="ai-analysis-section">
                  <div className="ai-analysis-header">🤖 AI智能解析（结合教材）</div>
                  <div className="ai-analysis-content">
                    <ReactMarkdown>{aiAnalysis.analysis}</ReactMarkdown>
                  </div>
                  {aiAnalysis.sources && aiAnalysis.sources.length > 0 && (
                    <div className="ai-sources">
                      <div className="sources-title">📚 参考来源：</div>
                      {aiAnalysis.sources.map((source, idx) => (
                        <div key={idx} className="source-item">
                          <div className="source-subject">{source.subject}</div>
                          <div className="source-content">{source.content}</div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          ) : (
            <div className="no-data">😔 暂无案例题</div>
          )
        )}
      </div>

      {/* 导航按钮 */}
      <div className="navigation">
        <button
          className="btn-nav btn-prev"
          onClick={handlePrev}
          disabled={currentIndex === 0}
        >
          ⬅️ 上一题
        </button>

        <div className="nav-info">
          {currentIndex + 1} / {activeTab === 'choice' ? questions.length : cases.length}
        </div>

        <button
          className="btn-nav btn-next"
          onClick={handleNext}
          disabled={currentIndex === (activeTab === 'choice' ? questions.length - 1 : cases.length - 1)}
        >
          下一题 ➡️
        </button>
      </div>
      </div>
    </div>
  )
}

export default ExamQuestions

