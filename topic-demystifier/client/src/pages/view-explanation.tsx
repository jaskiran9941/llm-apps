import { useQuery } from "@tanstack/react-query";
import { useParams, Link } from "wouter";
import { Header } from "@/components/header";
import { OutputDisplay } from "@/components/output-display";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Card } from "@/components/ui/card";
import { ArrowLeft, AlertCircle } from "lucide-react";
import type { Explanation } from "@shared/schema";

export default function ViewExplanation() {
  const params = useParams<{ id: string }>();
  const id = params.id;

  const { data, isLoading, error } = useQuery<{ success: boolean; data: Explanation }>({
    queryKey: ["/api/explanations", id],
  });

  const explanation = data?.data;

  return (
    <div className="min-h-screen bg-background">
      <Header showNewButton={true} />

      <main className="container mx-auto px-4 py-8 pb-16">
        <div className="mb-6">
          <Link href="/library">
            <Button variant="ghost" className="gap-2" data-testid="button-back-library">
              <ArrowLeft className="h-4 w-4" />
              Back to Library
            </Button>
          </Link>
        </div>

        {isLoading && (
          <div className="space-y-4">
            <Skeleton className="h-12 w-1/2" />
            <Skeleton className="h-6 w-3/4" />
            <Skeleton className="h-64 w-full" />
          </div>
        )}

        {error && (
          <Card className="p-12 text-center">
            <AlertCircle className="h-16 w-16 mx-auto text-destructive mb-4" />
            <h2 className="text-xl font-semibold mb-2">Failed to load explanation</h2>
            <p className="text-muted-foreground mb-6">
              This explanation may have been deleted or there was an error loading it.
            </p>
            <Link href="/library">
              <Button data-testid="button-return-library">Return to Library</Button>
            </Link>
          </Card>
        )}

        {!isLoading && !error && explanation && (
          <OutputDisplay
            explanation={{
              topic: explanation.topic,
              simpleSummary: explanation.simpleSummary,
              difficulty: explanation.difficulty as any,
              comicPanels: explanation.comicPanels,
              illustrations: explanation.illustrations,
              slides: explanation.slides,
              quiz: explanation.quiz || undefined,
            }}
            explanationId={explanation.id}
          />
        )}
      </main>
    </div>
  );
}
