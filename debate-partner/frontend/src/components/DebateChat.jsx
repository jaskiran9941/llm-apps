import { useEffect, useRef } from 'react'
import AudioPlayer from './AudioPlayer'
import './DebateChat.css'

function DebateChat({ messages, isLoading, onClearChat }) {
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  return (
    <div className="debate-chat">
      <div className="chat-header">
        <h2>Debate History</h2>
        {messages.length > 0 && (
          <button onClick={onClearChat} className="clear-btn">
            Clear Chat
          </button>
        )}
      </div>

      <div className="messages-container">
        {messages.length === 0 && (
          <div className="empty-state">
            <p>👋 Take a position on any topic</p>
            <p className="hint">I'll argue the opposite side to help you think critically</p>
          </div>
        )}

        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            <div className="message-header">
              <span className="role">
                {message.role === 'user' ? '🧑 You' : '🤖 Debate Partner'}
              </span>
              {message.isAudio && <span className="audio-badge">🎤 Voice</span>}
            </div>

            <div className="message-content">
              {message.content}
            </div>

            {message.audioUrl && (
              <AudioPlayer audioUrl={message.audioUrl} />
            )}
          </div>
        ))}

        {isLoading && (
          <div className="message assistant loading">
            <div className="message-header">
              <span className="role">🤖 Debate Partner</span>
            </div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>
    </div>
  )
}

export default DebateChat
