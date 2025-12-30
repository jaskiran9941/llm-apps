import { Link } from "wouter";
import { Home, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Header } from "@/components/header";

export default function NotFound() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-4 py-16 flex items-center justify-center">
        <div className="text-center space-y-6 max-w-md">
          <div className="h-24 w-24 mx-auto rounded-full bg-primary/10 flex items-center justify-center">
            <span className="font-display text-4xl font-bold text-primary">404</span>
          </div>
          
          <div className="space-y-2">
            <h1 className="font-display text-3xl font-bold">Page Not Found</h1>
            <p className="text-muted-foreground">
              The page you're looking for doesn't exist or has been moved.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <Button asChild>
              <Link href="/" data-testid="link-go-home">
                <Home className="mr-2 h-4 w-4" />
                Go Home
              </Link>
            </Button>
            <Button variant="outline" onClick={() => window.history.back()}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Go Back
            </Button>
          </div>
        </div>
      </main>
    </div>
  );
}
