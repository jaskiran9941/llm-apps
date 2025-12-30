import { useState } from "react";
import { X, ZoomIn } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import type { Illustration } from "@shared/schema";

interface IllustrationGalleryProps {
  illustrations: Illustration[];
}

export function IllustrationGallery({ illustrations }: IllustrationGalleryProps) {
  const [selectedIllustration, setSelectedIllustration] = useState<Illustration | null>(null);

  if (illustrations.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-muted-foreground">
        No illustrations available
      </div>
    );
  }

  return (
    <>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {illustrations.map((illustration) => (
          <IllustrationCard
            key={illustration.id}
            illustration={illustration}
            onClick={() => setSelectedIllustration(illustration)}
          />
        ))}
      </div>

      <Dialog open={!!selectedIllustration} onOpenChange={() => setSelectedIllustration(null)}>
        <DialogContent className="max-w-4xl p-0 overflow-hidden">
          {selectedIllustration && (
            <>
              <DialogHeader className="p-6 pb-0">
                <DialogTitle className="font-display text-xl">
                  {selectedIllustration.title}
                </DialogTitle>
              </DialogHeader>
              <div className="p-6">
                <div className="relative aspect-video bg-muted rounded-lg overflow-hidden mb-4">
                  {(selectedIllustration.imageBase64 || selectedIllustration.imageUrl) ? (
                    <img
                      src={selectedIllustration.imageBase64 || selectedIllustration.imageUrl}
                      alt={selectedIllustration.title}
                      className="w-full h-full object-contain"
                      data-testid={`img-illustration-full-${selectedIllustration.id}`}
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <span className="font-display text-8xl font-bold text-primary/10">
                        {selectedIllustration.id}
                      </span>
                    </div>
                  )}
                </div>
                <p className="text-muted-foreground leading-relaxed">
                  {selectedIllustration.description}
                </p>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}

interface IllustrationCardProps {
  illustration: Illustration;
  onClick: () => void;
}

function IllustrationCard({ illustration, onClick }: IllustrationCardProps) {
  const imageUrl = illustration.imageBase64 || illustration.imageUrl || null;

  return (
    <Card
      onClick={onClick}
      className="group cursor-pointer overflow-hidden transition-all duration-200 hover-elevate"
      data-testid={`card-illustration-${illustration.id}`}
    >
      <div className="aspect-square relative bg-gradient-to-br from-accent/20 to-primary/10 overflow-hidden">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt={illustration.title}
            className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="font-display text-7xl font-bold text-primary/20">
              {illustration.id}
            </span>
          </div>
        )}

        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex items-end justify-center pb-4">
          <div className="flex items-center gap-1 text-white text-sm font-medium">
            <ZoomIn className="h-4 w-4" />
            View full
          </div>
        </div>
      </div>

      <div className="p-4 space-y-1">
        <h4 className="font-display font-bold text-base line-clamp-1">{illustration.title}</h4>
        <p className="text-sm text-muted-foreground line-clamp-2">{illustration.description}</p>
      </div>
    </Card>
  );
}
