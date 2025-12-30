import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Header } from "@/components/header";
import { HeroSection } from "@/components/hero-section";
import { TopicInput } from "@/components/topic-input";
import { LoadingState } from "@/components/loading-state";
import { OutputDisplay } from "@/components/output-display";
import { useToast } from "@/hooks/use-toast";
import { apiRequest, queryClient } from "@/lib/queryClient";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { RefreshCw, Sparkles, Beaker, Cpu, Clock, Leaf, Coffee } from "lucide-react";
import type { ExplanationResponse, GenerationStatus, DifficultyLevel } from "@shared/schema";

interface TopicSuggestion {
  topic: string;
  description: string;
  category: string;
}

type AppState = "input" | "loading" | "result";

export default function Home() {
  const [appState, setAppState] = useState<AppState>("input");
  const [generationStatus, setGenerationStatus] = useState<GenerationStatus>({
    stage: "analyzing",
    progress: 0,
    message: "Starting...",
  });
  const [explanation, setExplanation] = useState<ExplanationResponse | null>(null);
  const { toast } = useToast();

  const generateMutation = useMutation({
    mutationFn: async (input: { text?: string; imageBase64?: string; difficulty: DifficultyLevel }) => {
      setAppState("loading");
      setGenerationStatus({
        stage: "analyzing",
        progress: 5,
        message: "Analyzing your topic...",
      });

      // Simulate progress updates while waiting for the API
      const progressStages = [
        { progress: 10, message: "Understanding your topic...", delay: 1500 },
        { progress: 20, message: "Researching key concepts...", delay: 2000 },
        { progress: 30, message: "Creating explanations...", delay: 3000 },
        { progress: 45, message: "Designing comic panels...", delay: 4000 },
        { progress: 55, message: "Generating illustrations...", delay: 5000 },
        { progress: 65, message: "Building slideshow...", delay: 6000 },
        { progress: 75, message: "Polishing content...", delay: 8000 },
        { progress: 85, message: "Almost there...", delay: 10000 },
        { progress: 90, message: "Final touches...", delay: 15000 },
      ];

      const timeouts: NodeJS.Timeout[] = [];
      let accumulatedDelay = 0;
      progressStages.forEach((stage) => {
        accumulatedDelay += stage.delay;
        const timeout = setTimeout(() => {
          setGenerationStatus({
            stage: "generating_comics",
            progress: stage.progress,
            message: stage.message,
          });
        }, accumulatedDelay);
        timeouts.push(timeout);
      });

      try {
        const response = await apiRequest("POST", "/api/explain", input);
        const data = await response.json();

        // Clear all pending timeouts when response arrives
        timeouts.forEach(clearTimeout);

        if (!data.success) {
          throw new Error(data.error || "Failed to generate explanation");
        }

        return data.data as ExplanationResponse;
      } catch (error) {
        // Clear timeouts on error too
        timeouts.forEach(clearTimeout);
        throw error;
      }
    },
    onSuccess: (data) => {
      setExplanation(data);
      setGenerationStatus({
        stage: "complete",
        progress: 100,
        message: "Your explanation is ready!",
      });
      setTimeout(() => {
        setAppState("result");
      }, 500);
    },
    onError: (error: Error) => {
      toast({
        title: "Something went wrong",
        description: error.message,
        variant: "destructive",
      });
      setGenerationStatus({
        stage: "error",
        progress: 0,
        message: error.message,
      });
      setTimeout(() => {
        setAppState("input");
      }, 2000);
    },
  });

  const saveMutation = useMutation({
    mutationFn: async (explanationData: ExplanationResponse) => {
      const response = await apiRequest("POST", "/api/explanations", explanationData);
      const data = await response.json();
      if (!data.success) {
        throw new Error(data.error || "Failed to save explanation");
      }
      return data.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/explanations"] });
      toast({
        title: "Saved!",
        description: "Explanation saved to your library",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Failed to save",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const handleSubmit = (input: { text?: string; imageBase64?: string; difficulty: DifficultyLevel }) => {
    generateMutation.mutate(input);
  };

  const handleSave = () => {
    if (explanation) {
      saveMutation.mutate(explanation);
    }
  };

  const handleNewExplanation = () => {
    setAppState("input");
    setExplanation(null);
    setGenerationStatus({
      stage: "analyzing",
      progress: 0,
      message: "Starting...",
    });
  };

  return (
    <div className="min-h-screen bg-background">
      <Header 
        onNewExplanation={handleNewExplanation} 
        showNewButton={appState === "result"} 
      />

      <main className="container mx-auto px-4 py-8 pb-16">
        {appState === "input" && (
          <div className="space-y-8">
            <HeroSection />
            <TopicInput 
              onSubmit={handleSubmit} 
              isLoading={generateMutation.isPending} 
            />
            <TopicSuggestions onSelect={(topic) => handleSubmit({ text: topic, difficulty: "age10" })} />
          </div>
        )}

        {appState === "loading" && (
          <div className="min-h-[60vh] flex items-center justify-center">
            <LoadingState status={generationStatus} />
          </div>
        )}

        {appState === "result" && explanation && (
          <OutputDisplay 
            explanation={explanation} 
            onSave={handleSave}
            isSaving={saveMutation.isPending}
          />
        )}
      </main>
    </div>
  );
}

interface TopicSuggestionsProps {
  onSelect: (topic: string) => void;
}

function getCategoryIcon(category: string) {
  switch (category.toLowerCase()) {
    case "science":
      return <Beaker className="w-3 h-3" />;
    case "technology":
      return <Cpu className="w-3 h-3" />;
    case "history":
      return <Clock className="w-3 h-3" />;
    case "nature":
      return <Leaf className="w-3 h-3" />;
    case "everyday":
      return <Coffee className="w-3 h-3" />;
    default:
      return <Sparkles className="w-3 h-3" />;
  }
}

function TopicSuggestions({ onSelect }: TopicSuggestionsProps) {
  const { data: suggestions, isLoading, isError, refetch, isFetching } = useQuery<TopicSuggestion[]>({
    queryKey: ["/api/topic-suggestions"],
    queryFn: async () => {
      const response = await fetch("/api/topic-suggestions");
      if (!response.ok) {
        throw new Error("Failed to fetch suggestions");
      }
      const result = await response.json();
      if (!result.success) {
        throw new Error(result.error || "Failed to fetch suggestions");
      }
      const data = result.data;
      if (!Array.isArray(data)) {
        throw new Error("Invalid suggestions format");
      }
      return data as TopicSuggestion[];
    },
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
  });

  if (isLoading) {
    return (
      <div className="w-full max-w-3xl mx-auto pt-8">
        <div className="flex items-center justify-center gap-2 mb-4">
          <Sparkles className="w-4 h-4 text-primary animate-pulse" />
          <p className="text-center text-sm text-muted-foreground">
            Generating topic suggestions...
          </p>
        </div>
        <div className="flex flex-wrap justify-center gap-2">
          {[...Array(6)].map((_, i) => (
            <Skeleton key={i} className="h-9 w-32 rounded-full" />
          ))}
        </div>
      </div>
    );
  }

  if (isError || !suggestions) {
    return (
      <div className="w-full max-w-3xl mx-auto pt-8">
        <p className="text-center text-sm text-muted-foreground mb-4">
          Could not load suggestions
        </p>
        <div className="flex justify-center">
          <Button
            variant="outline"
            size="sm"
            onClick={() => refetch()}
            data-testid="button-retry-suggestions"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Try again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-3xl mx-auto pt-8">
      <div className="flex items-center justify-center gap-2 mb-4">
        <Sparkles className="w-4 h-4 text-primary" />
        <p className="text-center text-sm text-muted-foreground">
          Explore these topics
        </p>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => refetch()}
          disabled={isFetching}
          className="ml-1"
          data-testid="button-refresh-suggestions"
        >
          <RefreshCw className={`w-4 h-4 ${isFetching ? "animate-spin" : ""}`} />
        </Button>
      </div>
      <div className="flex flex-wrap justify-center gap-2">
        {suggestions.map((suggestion, index) => (
          <button
            key={`${suggestion.topic}-${index}`}
            onClick={() => onSelect(suggestion.topic)}
            className="group flex items-center gap-2 px-4 py-2 text-sm bg-muted rounded-full transition-colors hover-elevate active-elevate-2"
            data-testid={`button-suggestion-${index}`}
            title={suggestion.description}
          >
            <span className="text-muted-foreground group-hover:text-foreground transition-colors">
              {getCategoryIcon(suggestion.category)}
            </span>
            <span>{suggestion.topic}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
