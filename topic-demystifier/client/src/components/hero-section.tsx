import { Sparkles, Lightbulb, BookOpen, Palette } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export function HeroSection() {
  return (
    <div className="relative overflow-hidden py-16 md:py-24">
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-accent/10" />
      
      <div className="absolute top-10 left-10 w-20 h-20 bg-primary/10 rounded-full blur-3xl" />
      <div className="absolute bottom-10 right-10 w-32 h-32 bg-accent/20 rounded-full blur-3xl" />
      <div className="absolute top-1/2 left-1/4 w-16 h-16 bg-primary/5 rounded-full blur-2xl" />

      <div className="relative container mx-auto px-4 text-center">
        <Badge variant="secondary" className="mb-6">
          <Sparkles className="mr-1 h-3 w-3" />
          Powered by AI
        </Badge>

        <h1 className="font-display text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold mb-6 bg-gradient-to-r from-foreground via-foreground to-foreground/70 bg-clip-text">
          Complex Topics,
          <br />
          <span className="text-primary">Simply Explained</span>
        </h1>

        <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-12 leading-relaxed">
          Enter any complex topic and get fun, easy-to-understand explanations through 
          AI-generated comics, illustrations, and interactive slideshows.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-6 text-sm text-muted-foreground">
          <FeatureHighlight icon={BookOpen} label="Comic Stories" />
          <FeatureHighlight icon={Palette} label="Visual Illustrations" />
          <FeatureHighlight icon={Lightbulb} label="Simple Explanations" />
        </div>
      </div>
    </div>
  );
}

interface FeatureHighlightProps {
  icon: React.ElementType;
  label: string;
}

function FeatureHighlight({ icon: Icon, label }: FeatureHighlightProps) {
  return (
    <div className="flex items-center gap-2">
      <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center">
        <Icon className="h-4 w-4 text-primary" />
      </div>
      <span className="font-medium">{label}</span>
    </div>
  );
}
