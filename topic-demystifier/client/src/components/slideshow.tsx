import { useState, useEffect, useRef, useCallback } from "react";
import {
  ChevronLeft,
  ChevronRight,
  Play,
  Pause,
  Volume2,
  VolumeX,
  SkipBack,
  SkipForward,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import type { Slide } from "@shared/schema";

interface SlideshowProps {
  slides: Slide[];
}

export function Slideshow({ slides }: SlideshowProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [ttsSupported, setTtsSupported] = useState(false);
  const speechSynthRef = useRef<SpeechSynthesisUtterance | null>(null);

  useEffect(() => {
    setTtsSupported(typeof window !== "undefined" && "speechSynthesis" in window);
  }, []);

  const currentSlide = slides[currentIndex];
  const progress = slides.length > 0 ? ((currentIndex + 1) / slides.length) * 100 : 0;

  const stopSpeaking = useCallback(() => {
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
    setIsSpeaking(false);
  }, []);

  const speakNarration = useCallback(
    (text: string) => {
      if (!ttsSupported || isMuted) return;

      stopSpeaking();

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9;
      utterance.pitch = 1;
      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => {
        setIsSpeaking(false);
        if (isPlaying && currentIndex < slides.length - 1) {
          setTimeout(() => {
            setCurrentIndex((prev) => prev + 1);
          }, 1000);
        } else if (isPlaying && currentIndex === slides.length - 1) {
          setIsPlaying(false);
        }
      };
      utterance.onerror = () => setIsSpeaking(false);

      speechSynthRef.current = utterance;
      window.speechSynthesis.speak(utterance);
    },
    [ttsSupported, isMuted, isPlaying, currentIndex, slides.length, stopSpeaking]
  );

  useEffect(() => {
    if (currentSlide?.narration && !isMuted) {
      const timer = setTimeout(() => {
        speakNarration(currentSlide.narration);
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [currentIndex, currentSlide?.narration, speakNarration, isMuted]);

  useEffect(() => {
    return () => stopSpeaking();
  }, [stopSpeaking]);

  const goToPrevious = () => {
    stopSpeaking();
    setCurrentIndex((prev) => (prev > 0 ? prev - 1 : 0));
  };

  const goToNext = () => {
    stopSpeaking();
    setCurrentIndex((prev) => (prev < slides.length - 1 ? prev + 1 : prev));
  };

  const togglePlay = () => {
    if (isPlaying) {
      stopSpeaking();
      setIsPlaying(false);
    } else {
      setIsPlaying(true);
      if (currentSlide?.narration) {
        speakNarration(currentSlide.narration);
      }
    }
  };

  const toggleMute = () => {
    if (!isMuted) {
      stopSpeaking();
    }
    setIsMuted(!isMuted);
  };

  const goToStart = () => {
    stopSpeaking();
    setCurrentIndex(0);
  };

  const goToEnd = () => {
    stopSpeaking();
    setCurrentIndex(slides.length - 1);
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "ArrowLeft") goToPrevious();
      if (e.key === "ArrowRight") goToNext();
      if (e.key === " ") {
        e.preventDefault();
        togglePlay();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isPlaying]);

  if (slides.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-muted-foreground">
        No slides available
      </div>
    );
  }

  const imageUrl = currentSlide.imageBase64 || currentSlide.imageUrl || null;

  return (
    <div className="w-full max-w-5xl mx-auto space-y-6">
      <div className="relative aspect-video bg-muted rounded-xl overflow-hidden shadow-lg">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt={currentSlide.title}
            className="w-full h-full object-contain"
            data-testid={`img-slide-${currentIndex}`}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-primary/10 to-accent/10">
            <span className="font-display text-8xl font-bold text-primary/20">
              {currentIndex + 1}
            </span>
          </div>
        )}

        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-6">
          <h3 className="font-display text-2xl md:text-3xl font-bold text-white mb-2">
            {currentSlide.title}
          </h3>
        </div>

        {isSpeaking && (
          <div className="absolute top-4 right-4 flex items-center gap-2 bg-primary text-primary-foreground px-3 py-1.5 rounded-full text-sm font-medium">
            <div className="flex gap-0.5">
              <span className="w-1 h-4 bg-current rounded-full animate-pulse" style={{ animationDelay: "0ms" }} />
              <span className="w-1 h-3 bg-current rounded-full animate-pulse" style={{ animationDelay: "150ms" }} />
              <span className="w-1 h-5 bg-current rounded-full animate-pulse" style={{ animationDelay: "300ms" }} />
              <span className="w-1 h-2 bg-current rounded-full animate-pulse" style={{ animationDelay: "450ms" }} />
            </div>
            Speaking
          </div>
        )}
      </div>

      <div className="bg-card rounded-xl p-6 space-y-4">
        <p className="text-base md:text-lg leading-relaxed text-center max-w-3xl mx-auto">
          {currentSlide.content}
        </p>

        {currentSlide.narration && (
          <p className="text-sm text-muted-foreground text-center italic max-w-2xl mx-auto">
            "{currentSlide.narration}"
          </p>
        )}
      </div>

      <div className="bg-card rounded-xl p-4 space-y-4">
        <Progress value={progress} className="h-1.5" />

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={goToStart}
              disabled={currentIndex === 0}
              data-testid="button-slide-start"
            >
              <SkipBack className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={goToPrevious}
              disabled={currentIndex === 0}
              data-testid="button-slide-prev"
            >
              <ChevronLeft className="h-5 w-5" />
            </Button>
          </div>

          <div className="flex items-center gap-4">
            <Button
              variant="default"
              size="icon"
              onClick={togglePlay}
              data-testid="button-slide-play"
            >
              {isPlaying ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5" />}
            </Button>

            <span className="text-sm font-medium min-w-[60px] text-center">
              {currentIndex + 1} / {slides.length}
            </span>

            <Button
              variant="ghost"
              size="icon"
              onClick={toggleMute}
              disabled={!ttsSupported}
              title={ttsSupported ? (isMuted ? "Unmute" : "Mute") : "Text-to-speech not supported in this browser"}
              data-testid="button-slide-mute"
            >
              {isMuted || !ttsSupported ? <VolumeX className="h-5 w-5" /> : <Volume2 className="h-5 w-5" />}
            </Button>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={goToNext}
              disabled={currentIndex === slides.length - 1}
              data-testid="button-slide-next"
            >
              <ChevronRight className="h-5 w-5" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={goToEnd}
              disabled={currentIndex === slides.length - 1}
              data-testid="button-slide-end"
            >
              <SkipForward className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
