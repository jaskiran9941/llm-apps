import { useState } from "react";
import { CheckCircle, XCircle, RefreshCw, Trophy, ChevronRight, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import type { QuizQuestion } from "@shared/schema";

interface QuizDisplayProps {
  questions: QuizQuestion[];
  isLoading?: boolean;
  onGenerateQuiz?: () => void;
}

export function QuizDisplay({ questions, isLoading, onGenerateQuiz }: QuizDisplayProps) {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, number>>({});
  const [showResult, setShowResult] = useState<Record<number, boolean>>({});
  const [quizComplete, setQuizComplete] = useState(false);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-4" data-testid="quiz-loading">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <p className="text-muted-foreground">Generating quiz questions...</p>
      </div>
    );
  }

  if (!questions || questions.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-4" data-testid="quiz-empty">
        <p className="text-muted-foreground text-center">
          No quiz available yet. Generate a quiz to test your understanding!
        </p>
        {onGenerateQuiz && (
          <Button onClick={onGenerateQuiz} data-testid="button-generate-quiz">
            Generate Quiz
          </Button>
        )}
      </div>
    );
  }

  const currentQuestion = questions[currentQuestionIndex];
  const totalQuestions = questions.length;
  const answeredCount = Object.keys(selectedAnswers).length;
  const progress = (answeredCount / totalQuestions) * 100;

  const handleSelectAnswer = (answerIndex: number) => {
    if (showResult[currentQuestionIndex]) return;

    setSelectedAnswers((prev) => ({
      ...prev,
      [currentQuestionIndex]: answerIndex,
    }));
    setShowResult((prev) => ({
      ...prev,
      [currentQuestionIndex]: true,
    }));
  };

  const handleNext = () => {
    if (currentQuestionIndex < totalQuestions - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else {
      setQuizComplete(true);
    }
  };

  const handleRestart = () => {
    setCurrentQuestionIndex(0);
    setSelectedAnswers({});
    setShowResult({});
    setQuizComplete(false);
  };

  const calculateScore = () => {
    let correct = 0;
    questions.forEach((q, idx) => {
      if (selectedAnswers[idx] === q.correctIndex) {
        correct++;
      }
    });
    return correct;
  };

  if (quizComplete) {
    const score = calculateScore();
    const percentage = Math.round((score / totalQuestions) * 100);
    
    return (
      <div className="max-w-2xl mx-auto" data-testid="quiz-results">
        <Card className="p-8">
          <div className="text-center space-y-6">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-primary/10">
              <Trophy className="h-10 w-10 text-primary" />
            </div>
            
            <div className="space-y-2">
              <h3 className="font-display text-2xl font-bold">Quiz Complete!</h3>
              <p className="text-muted-foreground">
                You've finished the quiz. Here's how you did:
              </p>
            </div>

            <div className="space-y-4">
              <div className="text-5xl font-bold font-display text-primary" data-testid="text-quiz-score">
                {score}/{totalQuestions}
              </div>
              <Progress value={percentage} className="h-3" />
              <p className="text-muted-foreground">
                {percentage >= 80
                  ? "Excellent work! You really understand this topic!"
                  : percentage >= 60
                  ? "Good job! You have a solid understanding."
                  : percentage >= 40
                  ? "Nice effort! Review the material and try again."
                  : "Keep learning! Review the explanation and try again."}
              </p>
            </div>

            <Button onClick={handleRestart} className="gap-2" data-testid="button-restart-quiz">
              <RefreshCw className="h-4 w-4" />
              Try Again
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  const selectedAnswer = selectedAnswers[currentQuestionIndex];
  const hasAnswered = showResult[currentQuestionIndex];
  const isCorrect = selectedAnswer === currentQuestion.correctIndex;

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="space-y-2">
        <div className="flex items-center justify-between gap-4 text-sm text-muted-foreground">
          <span data-testid="text-question-progress">Question {currentQuestionIndex + 1} of {totalQuestions}</span>
          <span>{answeredCount} answered</span>
        </div>
        <Progress value={progress} className="h-2" />
      </div>

      <Card className="p-6">
        <div className="space-y-6">
          <h3 className="font-display text-xl font-semibold" data-testid="text-question">
            {currentQuestion.question}
          </h3>

          <div className="space-y-3">
            {currentQuestion.options.map((option, idx) => {
              const isSelected = selectedAnswer === idx;
              const isCorrectOption = idx === currentQuestion.correctIndex;
              
              let optionClass = "border-border hover-elevate active-elevate-2";
              if (hasAnswered) {
                if (isCorrectOption) {
                  optionClass = "border-green-500 bg-green-50 dark:bg-green-950/30";
                } else if (isSelected && !isCorrectOption) {
                  optionClass = "border-red-500 bg-red-50 dark:bg-red-950/30";
                }
              } else if (isSelected) {
                optionClass = "border-primary bg-primary/5";
              }

              return (
                <button
                  key={idx}
                  onClick={() => handleSelectAnswer(idx)}
                  disabled={hasAnswered}
                  className={`w-full text-left p-4 rounded-lg border-2 transition-all flex items-center gap-3 ${optionClass} ${
                    hasAnswered ? "cursor-default" : "cursor-pointer"
                  }`}
                  data-testid={`button-option-${idx}`}
                >
                  <span className="flex-shrink-0 w-8 h-8 rounded-full border-2 border-current flex items-center justify-center text-sm font-medium">
                    {String.fromCharCode(65 + idx)}
                  </span>
                  <span className="flex-1">{option}</span>
                  {hasAnswered && isCorrectOption && (
                    <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0" />
                  )}
                  {hasAnswered && isSelected && !isCorrectOption && (
                    <XCircle className="h-5 w-5 text-red-600 flex-shrink-0" />
                  )}
                </button>
              );
            })}
          </div>

          {hasAnswered && (
            <div 
              className={`p-4 rounded-lg ${
                isCorrect 
                  ? "bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-800" 
                  : "bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800"
              }`}
              data-testid="text-explanation"
            >
              <p className="text-sm">
                <span className="font-semibold">
                  {isCorrect ? "Correct! " : "Not quite. "}
                </span>
                {currentQuestion.explanation}
              </p>
            </div>
          )}
        </div>
      </Card>

      <div className="flex justify-end">
        <Button
          onClick={handleNext}
          disabled={!hasAnswered}
          className="gap-2"
          data-testid="button-next-question"
        >
          {currentQuestionIndex < totalQuestions - 1 ? (
            <>
              Next Question
              <ChevronRight className="h-4 w-4" />
            </>
          ) : (
            "See Results"
          )}
        </Button>
      </div>
    </div>
  );
}
