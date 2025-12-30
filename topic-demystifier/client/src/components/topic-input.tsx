import { useState, useCallback } from "react";
import { Upload, FileText, Image, ArrowRight, X, Baby, GraduationCap, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import type { DifficultyLevel } from "@shared/schema";

interface TopicInputProps {
  onSubmit: (input: { text?: string; imageBase64?: string; difficulty: DifficultyLevel }) => void;
  isLoading?: boolean;
}

const difficultyOptions: { value: DifficultyLevel; label: string; description: string; icon: typeof Baby }[] = [
  { value: "age5", label: "Age 5", description: "Super simple", icon: Baby },
  { value: "age10", label: "Age 10", description: "Easy to follow", icon: GraduationCap },
  { value: "adult", label: "Adult", description: "Detailed", icon: User },
];

export function TopicInput({ onSubmit, isLoading = false }: TopicInputProps) {
  const [activeTab, setActiveTab] = useState<"text" | "image">("text");
  const [textInput, setTextInput] = useState("");
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [difficulty, setDifficulty] = useState<DifficultyLevel>("age10");

  const handleTextSubmit = () => {
    if (textInput.trim()) {
      onSubmit({ text: textInput.trim(), difficulty });
    }
  };

  const handleImageUpload = useCallback((file: File) => {
    if (file && file.type.startsWith("image/")) {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64 = reader.result as string;
        setImagePreview(base64);
      };
      reader.readAsDataURL(file);
    }
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) handleImageUpload(file);
    },
    [handleImageUpload]
  );

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) handleImageUpload(file);
    },
    [handleImageUpload]
  );

  const handleImageSubmit = () => {
    if (imagePreview) {
      onSubmit({ imageBase64: imagePreview, difficulty });
    }
  };

  const clearImage = () => {
    setImagePreview(null);
  };

  const characterCount = textInput.length;
  const maxCharacters = 1000;

  return (
    <Card className="w-full max-w-3xl mx-auto p-6 md:p-8">
      <div className="mb-6">
        <Label className="text-sm font-medium mb-3 block">Difficulty Level</Label>
        <div className="grid grid-cols-3 gap-2">
          {difficultyOptions.map((option) => {
            const Icon = option.icon;
            const isSelected = difficulty === option.value;
            return (
              <button
                key={option.value}
                onClick={() => setDifficulty(option.value)}
                disabled={isLoading}
                className={`flex flex-col items-center p-3 rounded-lg border-2 transition-colors ${
                  isSelected
                    ? "border-primary bg-primary/5"
                    : "border-muted hover-elevate"
                }`}
                data-testid={`button-difficulty-${option.value}`}
              >
                <Icon className={`h-5 w-5 mb-1 ${isSelected ? "text-primary" : "text-muted-foreground"}`} />
                <span className={`text-sm font-medium ${isSelected ? "text-primary" : ""}`}>{option.label}</span>
                <span className="text-xs text-muted-foreground">{option.description}</span>
              </button>
            );
          })}
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as "text" | "image")}>
        <TabsList className="grid w-full grid-cols-2 mb-6">
          <TabsTrigger value="text" className="gap-2" data-testid="tab-text-input">
            <FileText className="h-4 w-4" />
            <span>Text</span>
          </TabsTrigger>
          <TabsTrigger value="image" className="gap-2" data-testid="tab-image-input">
            <Image className="h-4 w-4" />
            <span>Image</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="text" className="mt-0">
          <div className="space-y-4">
            <div className="relative">
              <Textarea
                placeholder="Enter any complex topic you want explained simply... 

For example: 'How does quantum computing work?' or 'Explain blockchain technology'"
                className="min-h-[150px] text-base resize-none focus-visible:ring-2"
                value={textInput}
                onChange={(e) => setTextInput(e.target.value.slice(0, maxCharacters))}
                disabled={isLoading}
                data-testid="input-topic-text"
              />
              <span className="absolute bottom-3 right-3 text-sm text-muted-foreground">
                {characterCount}/{maxCharacters}
              </span>
            </div>
            <Button
              onClick={handleTextSubmit}
              disabled={!textInput.trim() || isLoading}
              className="w-full"
              size="lg"
              data-testid="button-submit-text"
            >
              {isLoading ? (
                <span className="flex items-center gap-2">
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                  Generating...
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  Explain This Topic
                  <ArrowRight className="h-4 w-4" />
                </span>
              )}
            </Button>
          </div>
        </TabsContent>

        <TabsContent value="image" className="mt-0">
          <div className="space-y-4">
            {!imagePreview ? (
              <div
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                className={`relative flex min-h-[200px] cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed transition-colors ${
                  isDragging
                    ? "border-primary bg-primary/5"
                    : "border-muted-foreground/25 hover:border-primary/50"
                }`}
                data-testid="dropzone-image"
              >
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileSelect}
                  className="absolute inset-0 cursor-pointer opacity-0"
                  disabled={isLoading}
                  data-testid="input-image-file"
                />
                <Upload className="mb-3 h-10 w-10 text-muted-foreground" />
                <p className="text-base font-medium">
                  Drop an image here or click to upload
                </p>
                <p className="mt-1 text-sm text-muted-foreground">
                  PNG, JPG, GIF up to 10MB
                </p>
              </div>
            ) : (
              <div className="relative rounded-xl overflow-hidden">
                <img
                  src={imagePreview}
                  alt="Preview"
                  className="w-full h-auto max-h-[300px] object-contain bg-muted"
                  data-testid="img-preview"
                />
                <Button
                  variant="secondary"
                  size="icon"
                  className="absolute top-2 right-2"
                  onClick={clearImage}
                  disabled={isLoading}
                  data-testid="button-clear-image"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            )}
            <Button
              onClick={handleImageSubmit}
              disabled={!imagePreview || isLoading}
              className="w-full"
              size="lg"
              data-testid="button-submit-image"
            >
              {isLoading ? (
                <span className="flex items-center gap-2">
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                  Analyzing...
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  Explain This Image
                  <ArrowRight className="h-4 w-4" />
                </span>
              )}
            </Button>
          </div>
        </TabsContent>
      </Tabs>
    </Card>
  );
}
