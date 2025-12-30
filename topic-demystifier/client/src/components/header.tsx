import { Sparkles, Plus, BookOpen } from "lucide-react";
import { Link, useLocation } from "wouter";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/theme-toggle";

interface HeaderProps {
  onNewExplanation?: () => void;
  showNewButton?: boolean;
}

export function Header({ onNewExplanation, showNewButton = false }: HeaderProps) {
  const [location] = useLocation();

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-14 items-center justify-between gap-4 px-4">
        <Link href="/" className="flex items-center gap-2" data-testid="link-home">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
            <Sparkles className="h-5 w-5 text-primary-foreground" />
          </div>
          <span className="font-display text-xl font-bold">ExplainIt</span>
        </Link>

        <div className="flex items-center gap-2">
          {location !== "/library" && (
            <Link href="/library">
              <Button variant="ghost" size="sm" className="gap-1" data-testid="button-library">
                <BookOpen className="h-4 w-4" />
                <span className="hidden sm:inline">Library</span>
              </Button>
            </Link>
          )}
          {showNewButton && onNewExplanation && (
            <Button
              onClick={onNewExplanation}
              variant="outline"
              size="sm"
              data-testid="button-new-explanation"
            >
              <Plus className="mr-1 h-4 w-4" />
              New
            </Button>
          )}
          {showNewButton && !onNewExplanation && (
            <Link href="/">
              <Button variant="outline" size="sm" data-testid="button-new-explanation">
                <Plus className="mr-1 h-4 w-4" />
                New
              </Button>
            </Link>
          )}
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
