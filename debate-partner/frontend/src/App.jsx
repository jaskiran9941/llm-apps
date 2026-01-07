import { useState } from 'react'
import './App.css'
import DebateChat from './components/DebateChat'
import AudioRecorder from './components/AudioRecorder'

function App() {
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)

  const handleTextMessage = async (text) => {
    // Add user message
    const userMessage = {
      role: 'user',
      content: text,
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    try {
      // Build conversation history for API
      const history = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }))

      const response = await fetch('http://localhost:8000/api/debate/text', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: text,
          conversation_history: history
        })
      })

      if (!response.ok) throw new Error('Failed to get response')

      const data = await response.json()

      // Add assistant message
      const assistantMessage = {
        role: 'assistant',
        content: data.text,
        audioUrl: `http://localhost:8000${data.audio_url}`,
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, assistantMessage])

    } catch (error) {
      console.error('Error:', error)
      alert('Failed to get debate response. Check console for details.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleAudioMessage = async (audioBlob) => {
    setIsLoading(true)

    try {
      const formData = new FormData()
      formData.append('audio', audioBlob, 'recording.webm')

      // Build conversation history
      const history = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }))
      formData.append('conversation_history', JSON.stringify(history))

      const response = await fetch('http://localhost:8000/api/debate/audio', {
        method: 'POST',
        body: formData
      })

      if (!response.ok) throw new Error('Failed to get response')

      const data = await response.json()

      // Add user message (transcribed)
      const userMessage = {
        role: 'user',
        content: data.transcribed_input,
        timestamp: new Date().toISOString(),
        isAudio: true
      }
      setMessages(prev => [...prev, userMessage])

      // Add assistant message
      const assistantMessage = {
        role: 'assistant',
        content: data.text,
        audioUrl: `http://localhost:8000${data.audio_url}`,
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, assistantMessage])

    } catch (error) {
      console.error('Error:', error)
      alert('Failed to process audio. Check console for details.')
    } finally {
      setIsLoading(false)
    }
  }

  const clearChat = () => {
    setMessages([])
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🎙️ Debate Partner</h1>
        <p>I'll argue the opposite side of any position you take</p>
      </header>

      <div className="app-container">
        <DebateChat
          messages={messages}
          isLoading={isLoading}
          onClearChat={clearChat}
        />

        <div className="input-section">
          <AudioRecorder
            onRecordingComplete={handleAudioMessage}
            disabled={isLoading}
          />

          <div className="text-input-container">
            <form onSubmit={(e) => {
              e.preventDefault()
              const text = e.target.message.value.trim()
              if (text) {
                handleTextMessage(text)
                e.target.reset()
              }
            }}>
              <textarea
                name="message"
                placeholder="Or type your position here..."
                disabled={isLoading}
                rows="3"
              />
              <button type="submit" disabled={isLoading}>
                {isLoading ? 'Thinking...' : 'Send'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
