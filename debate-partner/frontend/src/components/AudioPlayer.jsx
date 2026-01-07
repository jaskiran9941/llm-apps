import { useState, useRef } from 'react'
import './AudioPlayer.css'

function AudioPlayer({ audioUrl }) {
  const [isPlaying, setIsPlaying] = useState(false)
  const audioRef = useRef(null)

  const togglePlayPause = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause()
      } else {
        audioRef.current.play()
      }
      setIsPlaying(!isPlaying)
    }
  }

  const handleEnded = () => {
    setIsPlaying(false)
  }

  return (
    <div className="audio-player">
      <audio
        ref={audioRef}
        src={audioUrl}
        onEnded={handleEnded}
      />
      <button onClick={togglePlayPause} className="play-btn">
        {isPlaying ? '⏸️ Pause' : '▶️ Play Response'}
      </button>
    </div>
  )
}

export default AudioPlayer
