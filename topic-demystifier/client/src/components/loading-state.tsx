import { Sparkles, BookOpen, Palette, Presentation, CheckCircle } from "lucide-react";
import { Progress } from "@/components/ui/progress";
import type { GenerationStatus } from "@shared/schema";

interface LoadingStateProps {
  status: GenerationStatus;
}

const stageConfig = {
  analyzing: {
    icon: Sparkles,
    label: "Analyzing Topic",
    description: "Understanding what you want to learn about...",
  },
  explaining: {
    icon: BookOpen,
    label: "Creating Explanation",
    description: "Breaking down complex concepts into simple terms...",
  },
  generating_comics: {
    icon: Palette,
    label: "Drawing Comics",
    description: "Creating fun comic panels to illustrate the concept...",
  },
  generating_illustrations: {
    icon: Palette,
    label: "Creating Illustrations",
    description: "Generating visual illustrations for key concepts...",
  },
  generating_slides: {
    icon: Presentation,
    label: "Building Slideshow",
    description: "Preparing your slideshow presentation...",
  },
  complete: {
    icon: CheckCircle,
    label: "Complete",
    description: "Your explanation is ready!",
  },
  error: {
    icon: Sparkles,
    label: "Error",
    description: "Something went wrong. Please try again.",
  },
};

export function LoadingState({ status }: LoadingStateProps) {
  const config = stageConfig[status.stage];
  const Icon = config.icon;

  return (
    <div className="w-full max-w-xl mx-auto p-8">
      <div className="flex flex-col items-center text-center space-y-6">
        <div className="relative">
          <div className="h-20 w-20 rounded-full bg-primary/10 flex items-center justify-center">
            <Icon className="h-10 w-10 text-primary animate-pulse" />
          </div>
          {status.stage !== "complete" && status.stage !== "error" && (
            <div className="absolute inset-0 h-20 w-20 rounded-full border-4 border-primary/30 border-t-primary animate-spin" />
          )}
        </div>

        <div className="space-y-2">
          <h3 className="font-display text-2xl font-bold">{config.label}</h3>
          <p className="text-muted-foreground">{status.message || config.description}</p>
        </div>

        <div className="w-full space-y-2">
          <Progress value={status.progress} className="h-2" />
          <p className="text-sm text-muted-foreground">{Math.round(status.progress)}% complete</p>
        </div>

        <div className="flex items-center gap-4 text-sm text-muted-foreground pt-4">
          <StageIndicator 
            label="Analyze" 
            active={status.stage === "analyzing"} 
            complete={["explaining", "generating_comics", "generating_illustrations", "generating_slides", "complete"].includes(status.stage)} 
          />
          <StageIndicator 
            label="Explain" 
            active={status.stage === "explaining"} 
            complete={["generating_comics", "generating_illustrations", "generating_slides", "complete"].includes(status.stage)} 
          />
          <StageIndicator 
            label="Create" 
            active={["generating_comics", "generating_illustrations", "generating_slides"].includes(status.stage)} 
            complete={status.stage === "complete"} 
          />
          <StageIndicator 
            label="Done" 
            active={status.stage === "complete"} 
            complete={false} 
          />
        </div>
      </div>
    </div>
  );
}

interface StageIndicatorProps {
  label: string;
  active: boolean;
  complete: boolean;
}

function StageIndicator({ label, active, complete }: StageIndicatorProps) {
  return (
    <div className="flex flex-col items-center gap-1">
      <div
        className={`h-3 w-3 rounded-full transition-colors ${
          complete
            ? "bg-primary"
            : active
            ? "bg-primary animate-pulse"
            : "bg-muted"
        }`}
      />
      <span className={active || complete ? "text-foreground font-medium" : ""}>{label}</span>
    </div>
  );
}
