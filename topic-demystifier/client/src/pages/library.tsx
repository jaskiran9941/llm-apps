import { useQuery, useMutation } from "@tanstack/react-query";
import { Link } from "wouter";
import { Header } from "@/components/header";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowLeft, Trash2, Eye, BookOpen, Calendar, Baby, GraduationCap, User } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { apiRequest, queryClient } from "@/lib/queryClient";
import type { Explanation } from "@shared/schema";
import { formatDistanceToNow } from "date-fns";

const difficultyLabels: Record<string, { label: string; icon: typeof Baby }> = {
  age5: { label: "Age 5", icon: Baby },
  age10: { label: "Age 10", icon: GraduationCap },
  adult: { label: "Adult", icon: User },
};

export default function Library() {
  const { toast } = useToast();

  const { data, isLoading, error } = useQuery<{ success: boolean; data: Explanation[] }>({
    queryKey: ["/api/explanations"],
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      const response = await apiRequest("DELETE", `/api/explanations/${id}`);
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/explanations"] });
      toast({
        title: "Deleted",
        description: "Explanation removed from your library",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const explanations = data?.data || [];

  return (
    <div className="min-h-screen bg-background">
      <Header showNewButton={false} />

      <main className="container mx-auto px-4 py-8 pb-16">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
          <div className="flex items-center gap-4">
            <Link href="/">
              <Button variant="ghost" size="icon" data-testid="button-back-home">
                <ArrowLeft className="h-5 w-5" />
              </Button>
            </Link>
            <div>
              <h1 className="text-2xl md:text-3xl font-bold flex items-center gap-2">
                <BookOpen className="h-7 w-7" />
                My Library
              </h1>
              <p className="text-muted-foreground">Your saved explanations</p>
            </div>
          </div>
          <Link href="/">
            <Button data-testid="button-create-new">
              Create New Explanation
            </Button>
          </Link>
        </div>

        {isLoading && (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <Card key={i}>
                <CardHeader>
                  <Skeleton className="h-6 w-3/4" />
                  <Skeleton className="h-4 w-1/2 mt-2" />
                </CardHeader>
                <CardContent>
                  <Skeleton className="h-20 w-full" />
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {error && (
          <Card className="p-8 text-center">
            <p className="text-destructive">Failed to load your library. Please try again.</p>
          </Card>
        )}

        {!isLoading && !error && explanations.length === 0 && (
          <Card className="p-12 text-center">
            <BookOpen className="h-16 w-16 mx-auto text-muted-foreground mb-4" />
            <h2 className="text-xl font-semibold mb-2">Your library is empty</h2>
            <p className="text-muted-foreground mb-6">
              Start exploring topics and save your favorite explanations here!
            </p>
            <Link href="/">
              <Button data-testid="button-start-exploring">Start Exploring</Button>
            </Link>
          </Card>
        )}

        {!isLoading && !error && explanations.length > 0 && (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {explanations.map((explanation) => {
              const DifficultyIcon = difficultyLabels[explanation.difficulty]?.icon || GraduationCap;
              return (
                <Card key={explanation.id} className="overflow-hidden hover-elevate" data-testid={`card-explanation-${explanation.id}`}>
                  {explanation.comicPanels[0]?.imageBase64 && (
                    <div className="h-32 overflow-hidden bg-muted">
                      <img
                        src={explanation.comicPanels[0].imageBase64}
                        alt={explanation.topic}
                        className="w-full h-full object-cover"
                      />
                    </div>
                  )}
                  <CardHeader className="pb-2">
                    <div className="flex flex-wrap items-start justify-between gap-2">
                      <CardTitle className="text-lg line-clamp-2">{explanation.topic}</CardTitle>
                      <Badge variant="secondary" className="shrink-0">
                        <DifficultyIcon className="h-3 w-3 mr-1" />
                        {difficultyLabels[explanation.difficulty]?.label || "Age 10"}
                      </Badge>
                    </div>
                    <CardDescription className="flex items-center gap-1 text-xs">
                      <Calendar className="h-3 w-3" />
                      {formatDistanceToNow(new Date(explanation.createdAt), { addSuffix: true })}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground line-clamp-3 mb-4">
                      {explanation.simpleSummary}
                    </p>
                    <div className="flex flex-wrap gap-2">
                      <Link href={`/explanation/${explanation.id}`}>
                        <Button variant="outline" size="sm" className="gap-1" data-testid={`button-view-${explanation.id}`}>
                          <Eye className="h-4 w-4" />
                          View
                        </Button>
                      </Link>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="gap-1 text-destructive"
                        onClick={() => deleteMutation.mutate(explanation.id)}
                        disabled={deleteMutation.isPending}
                        data-testid={`button-delete-${explanation.id}`}
                      >
                        <Trash2 className="h-4 w-4" />
                        Delete
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}
