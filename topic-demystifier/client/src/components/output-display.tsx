import { useState } from "react";
import { BookOpen, Image, Presentation, Save, Baby, GraduationCap, User, HelpCircle } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ComicStrip } from "@/components/comic-strip";
import { IllustrationGallery } from "@/components/illustration-gallery";
import { Slideshow } from "@/components/slideshow";
import { QuizDisplay } from "@/components/quiz-display";
import { ShareButtons } from "@/components/share-buttons";
import { apiRequest } from "@/lib/queryClient";
import type { ExplanationResponse, DifficultyLevel, QuizQuestion } from "@shared/schema";

interface OutputDisplayProps {
  explanation: ExplanationResponse;
  explanationId?: number;
  onSave?: () => void;
  isSaving?: boolean;
}

const difficultyLabels: Record<DifficultyLevel, { label: string; icon: typeof Baby }> = {
  age5: { label: "Age 5", icon: Baby },
  age10: { label: "Age 10", icon: GraduationCap },
  adult: { label: "Adult", icon: User },
};

export function OutputDisplay({ explanation, explanationId, onSave, isSaving }: OutputDisplayProps) {
  const [quiz, setQuiz] = useState<QuizQuestion[]>(explanation.quiz || []);
  const [isGeneratingQuiz, setIsGeneratingQuiz] = useState(false);

  const difficulty = explanation.difficulty || "age10";
  const DifficultyIcon = difficultyLabels[difficulty]?.icon || GraduationCap;

  const handleGenerateQuiz = async () => {
    setIsGeneratingQuiz(true);
    try {
      const response = await apiRequest("POST", "/api/quiz/generate", {
        topic: explanation.topic,
        summary: explanation.simpleSummary,
        difficulty: explanation.difficulty,
      });
      
      const data = await response.json();
      if (data.success && data.data) {
        setQuiz(data.data);
      }
    } catch (error) {
      console.error("Failed to generate quiz:", error);
    } finally {
      setIsGeneratingQuiz(false);
    }
  };

  return (
    <div className="w-full max-w-6xl mx-auto space-y-8">
      <div className="text-center space-y-4">
        <div className="flex flex-wrap items-center justify-center gap-2">
          <Badge variant="secondary" className="text-xs">
            Explained Simply
          </Badge>
          <Badge variant="outline" className="text-xs gap-1">
            <DifficultyIcon className="h-3 w-3" />
            {difficultyLabels[difficulty]?.label || "Age 10"}
          </Badge>
        </div>
        <h2 className="font-display text-3xl md:text-4xl font-bold">{explanation.topic}</h2>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed">
          {explanation.simpleSummary}
        </p>
        <div className="flex flex-wrap items-center justify-center gap-3 mt-4">
          {onSave && (
            <Button 
              onClick={onSave} 
              disabled={isSaving}
              variant="outline"
              data-testid="button-save-explanation"
            >
              {isSaving ? (
                <span className="flex items-center gap-2">
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                  Saving...
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  <Save className="h-4 w-4" />
                  Save to Library
                </span>
              )}
            </Button>
          )}
          {explanationId && (
            <ShareButtons explanationId={explanationId} topic={explanation.topic} />
          )}
        </div>
      </div>

      <Tabs defaultValue="comic" className="w-full">
        <TabsList className="grid w-full max-w-lg mx-auto grid-cols-4">
          <TabsTrigger value="comic" className="gap-2" data-testid="tab-output-comic">
            <BookOpen className="h-4 w-4" />
            <span className="hidden sm:inline">Comic</span>
          </TabsTrigger>
          <TabsTrigger value="illustrations" className="gap-2" data-testid="tab-output-illustrations">
            <Image className="h-4 w-4" />
            <span className="hidden sm:inline">Gallery</span>
          </TabsTrigger>
          <TabsTrigger value="slideshow" className="gap-2" data-testid="tab-output-slideshow">
            <Presentation className="h-4 w-4" />
            <span className="hidden sm:inline">Slides</span>
          </TabsTrigger>
          <TabsTrigger value="quiz" className="gap-2" data-testid="tab-output-quiz">
            <HelpCircle className="h-4 w-4" />
            <span className="hidden sm:inline">Quiz</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="comic" className="mt-8">
          <ComicStrip 
            panels={explanation.comicPanels} 
            topic={explanation.topic}
            summary={explanation.simpleSummary}
          />
        </TabsContent>

        <TabsContent value="illustrations" className="mt-8">
          <IllustrationGallery illustrations={explanation.illustrations} />
        </TabsContent>

        <TabsContent value="slideshow" className="mt-8">
          <Slideshow slides={explanation.slides} />
        </TabsContent>

        <TabsContent value="quiz" className="mt-8">
          <QuizDisplay
            questions={quiz}
            isLoading={isGeneratingQuiz}
            onGenerateQuiz={handleGenerateQuiz}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
}
