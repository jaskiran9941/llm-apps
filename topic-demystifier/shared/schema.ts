import { z } from "zod";
import { pgTable, serial, text, timestamp, jsonb, varchar } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";

// Difficulty levels for explanations
export const difficultyLevels = ["age5", "age10", "adult"] as const;
export type DifficultyLevel = typeof difficultyLevels[number];

// Input types for topic explanation
export const topicInputSchema = z.object({
  text: z.string().optional(),
  imageBase64: z.string().optional(),
  difficulty: z.enum(difficultyLevels).default("age10"),
});

export type TopicInput = z.infer<typeof topicInputSchema>;

// Comic panel structure
export const comicPanelSchema = z.object({
  id: z.number(),
  title: z.string(),
  description: z.string(),
  imageUrl: z.string().optional(),
  imageBase64: z.string().optional(),
  speechBubble: z.string(),
});

export type ComicPanel = z.infer<typeof comicPanelSchema>;

// Illustration structure
export const illustrationSchema = z.object({
  id: z.number(),
  title: z.string(),
  description: z.string(),
  imageUrl: z.string().optional(),
  imageBase64: z.string().optional(),
});

export type Illustration = z.infer<typeof illustrationSchema>;

// Slideshow slide structure
export const slideSchema = z.object({
  id: z.number(),
  title: z.string(),
  content: z.string(),
  imageUrl: z.string().optional(),
  imageBase64: z.string().optional(),
  narration: z.string(),
});

export type Slide = z.infer<typeof slideSchema>;

// Quiz question structure
export const quizQuestionSchema = z.object({
  id: z.number(),
  question: z.string(),
  options: z.array(z.string()),
  correctIndex: z.number(),
  explanation: z.string(),
});

export type QuizQuestion = z.infer<typeof quizQuestionSchema>;

// Full explanation response
export const explanationResponseSchema = z.object({
  topic: z.string(),
  simpleSummary: z.string(),
  difficulty: z.enum(difficultyLevels).optional(),
  comicPanels: z.array(comicPanelSchema),
  illustrations: z.array(illustrationSchema),
  slides: z.array(slideSchema),
  quiz: z.array(quizQuestionSchema).optional(),
});

export type ExplanationResponse = z.infer<typeof explanationResponseSchema>;

// API response wrapper
export const apiResponseSchema = z.object({
  success: z.boolean(),
  data: explanationResponseSchema.optional(),
  error: z.string().optional(),
});

export type ApiResponse = z.infer<typeof apiResponseSchema>;

// Generation status for progress tracking
export const generationStatusSchema = z.object({
  stage: z.enum(["analyzing", "explaining", "generating_comics", "generating_illustrations", "generating_slides", "generating_quiz", "complete", "error"]),
  progress: z.number().min(0).max(100),
  message: z.string(),
});

export type GenerationStatus = z.infer<typeof generationStatusSchema>;

// Database table for saved explanations
export const explanations = pgTable("explanations", {
  id: serial("id").primaryKey(),
  topic: text("topic").notNull(),
  difficulty: varchar("difficulty", { length: 20 }).notNull().default("age10"),
  simpleSummary: text("simple_summary").notNull(),
  comicPanels: jsonb("comic_panels").notNull().$type<ComicPanel[]>(),
  illustrations: jsonb("illustrations").notNull().$type<Illustration[]>(),
  slides: jsonb("slides").notNull().$type<Slide[]>(),
  quiz: jsonb("quiz").$type<QuizQuestion[]>(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const insertExplanationSchema = z.object({
  topic: z.string(),
  difficulty: z.enum(difficultyLevels).default("age10"),
  simpleSummary: z.string(),
  comicPanels: z.array(comicPanelSchema),
  illustrations: z.array(illustrationSchema),
  slides: z.array(slideSchema),
  quiz: z.array(quizQuestionSchema).optional(),
});
export type InsertExplanation = z.infer<typeof insertExplanationSchema>;
export type Explanation = typeof explanations.$inferSelect;

// User types (keeping existing structure)
export const insertUserSchema = z.object({
  username: z.string(),
  password: z.string(),
});

export type InsertUser = z.infer<typeof insertUserSchema>;
export type User = { id: string; username: string; password: string };
