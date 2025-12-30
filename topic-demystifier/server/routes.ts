import type { Express } from "express";
import { createServer, type Server } from "http";
import { 
  analyzeImageTopic, 
  generateExplanation, 
  generateAllImages,
  generateQuiz,
  generateTopicSuggestions,
  type ExplanationContent 
} from "./openai";
import { topicInputSchema, insertExplanationSchema, type DifficultyLevel } from "@shared/schema";
import type { ExplanationResponse, ComicPanel, Illustration, Slide, QuizQuestion } from "@shared/schema";
import { storage } from "./storage";

export async function registerRoutes(
  httpServer: Server,
  app: Express
): Promise<Server> {
  
  app.post("/api/explain", async (req, res) => {
    try {
      const parseResult = topicInputSchema.safeParse(req.body);
      
      if (!parseResult.success) {
        return res.status(400).json({
          success: false,
          error: "Invalid input format"
        });
      }
      
      const { text, imageBase64, difficulty } = parseResult.data;
      
      if (!text?.trim() && !imageBase64) {
        return res.status(400).json({
          success: false,
          error: "Please provide a topic (text or image)"
        });
      }

      // Step 1: Determine the topic
      let topic: string;
      if (imageBase64) {
        console.log("Analyzing image to extract topic...");
        topic = await analyzeImageTopic(imageBase64);
      } else {
        topic = text!;
      }
      
      console.log(`Generating explanation for topic: ${topic} at difficulty: ${difficulty}`);
      
      // Step 2: Generate the explanation content with difficulty level
      const explanationContent = await generateExplanation(topic, difficulty as DifficultyLevel);
      console.log("Explanation content generated, now generating images...");
      
      // Step 3: Collect all image prompts
      const imagePrompts: { id: number; prompt: string; type: "comic" | "illustration" | "slide" }[] = [];
      
      explanationContent.comicPanels.forEach((panel) => {
        imagePrompts.push({
          id: panel.id,
          prompt: panel.imagePrompt,
          type: "comic"
        });
      });
      
      explanationContent.illustrations.forEach((illustration) => {
        imagePrompts.push({
          id: illustration.id,
          prompt: illustration.imagePrompt,
          type: "illustration"
        });
      });
      
      explanationContent.slides.forEach((slide) => {
        imagePrompts.push({
          id: slide.id,
          prompt: slide.imagePrompt,
          type: "slide"
        });
      });
      
      // Step 4: Generate all images
      const images = await generateAllImages(imagePrompts);
      console.log(`Generated ${images.size} images`);
      
      // Step 5: Assemble the final response
      const comicPanels: ComicPanel[] = explanationContent.comicPanels.map((panel) => ({
        id: panel.id,
        title: panel.title,
        description: panel.description,
        speechBubble: panel.speechBubble,
        imageBase64: images.get(`comic-${panel.id}`)
      }));
      
      const illustrations: Illustration[] = explanationContent.illustrations.map((illustration) => ({
        id: illustration.id,
        title: illustration.title,
        description: illustration.description,
        imageBase64: images.get(`illustration-${illustration.id}`)
      }));
      
      const slides: Slide[] = explanationContent.slides.map((slide) => ({
        id: slide.id,
        title: slide.title,
        content: slide.content,
        narration: slide.narration,
        imageBase64: images.get(`slide-${slide.id}`)
      }));
      
      const response: ExplanationResponse = {
        topic: explanationContent.topic,
        simpleSummary: explanationContent.simpleSummary,
        difficulty,
        comicPanels,
        illustrations,
        slides
      };
      
      console.log("Explanation complete, sending response");
      
      return res.json({
        success: true,
        data: response
      });
      
    } catch (error: any) {
      console.error("Error generating explanation:", error);
      return res.status(500).json({
        success: false,
        error: error.message || "Failed to generate explanation"
      });
    }
  });

  // Save explanation to library
  app.post("/api/explanations", async (req, res) => {
    try {
      const parseResult = insertExplanationSchema.safeParse(req.body);
      
      if (!parseResult.success) {
        return res.status(400).json({
          success: false,
          error: "Invalid explanation data: " + parseResult.error.errors.map(e => e.message).join(", ")
        });
      }

      const saved = await storage.saveExplanation(parseResult.data);

      return res.json({
        success: true,
        data: saved
      });
    } catch (error: any) {
      console.error("Error saving explanation:", error);
      return res.status(500).json({
        success: false,
        error: error.message || "Failed to save explanation"
      });
    }
  });

  // Get all saved explanations
  app.get("/api/explanations", async (_req, res) => {
    try {
      const explanations = await storage.getAllExplanations();
      return res.json({
        success: true,
        data: explanations
      });
    } catch (error: any) {
      console.error("Error fetching explanations:", error);
      return res.status(500).json({
        success: false,
        error: error.message || "Failed to fetch explanations"
      });
    }
  });

  // Get single explanation by ID
  app.get("/api/explanations/:id", async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      if (isNaN(id)) {
        return res.status(400).json({
          success: false,
          error: "Invalid ID"
        });
      }

      const explanation = await storage.getExplanation(id);
      if (!explanation) {
        return res.status(404).json({
          success: false,
          error: "Explanation not found"
        });
      }

      return res.json({
        success: true,
        data: explanation
      });
    } catch (error: any) {
      console.error("Error fetching explanation:", error);
      return res.status(500).json({
        success: false,
        error: error.message || "Failed to fetch explanation"
      });
    }
  });

  // Delete explanation
  app.delete("/api/explanations/:id", async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      if (isNaN(id)) {
        return res.status(400).json({
          success: false,
          error: "Invalid ID"
        });
      }

      const deleted = await storage.deleteExplanation(id);
      if (!deleted) {
        return res.status(404).json({
          success: false,
          error: "Explanation not found"
        });
      }

      return res.json({
        success: true,
        message: "Explanation deleted"
      });
    } catch (error: any) {
      console.error("Error deleting explanation:", error);
      return res.status(500).json({
        success: false,
        error: error.message || "Failed to delete explanation"
      });
    }
  });

  // Generate quiz for an explanation
  app.post("/api/explanations/:id/quiz", async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      if (isNaN(id)) {
        return res.status(400).json({
          success: false,
          error: "Invalid ID"
        });
      }

      const explanation = await storage.getExplanation(id);
      if (!explanation) {
        return res.status(404).json({
          success: false,
          error: "Explanation not found"
        });
      }

      // If quiz already exists, return it
      if (explanation.quiz && explanation.quiz.length > 0) {
        return res.json({
          success: true,
          data: explanation.quiz
        });
      }

      console.log(`Generating quiz for explanation: ${explanation.topic}`);
      
      const quiz = await generateQuiz(
        explanation.topic, 
        explanation.simpleSummary,
        (explanation.difficulty as DifficultyLevel) || "age10"
      );

      // Save the quiz to the database
      await storage.updateExplanationQuiz(id, quiz);

      console.log(`Quiz generated with ${quiz.length} questions`);

      return res.json({
        success: true,
        data: quiz
      });
    } catch (error: any) {
      console.error("Error generating quiz:", error);
      return res.status(500).json({
        success: false,
        error: error.message || "Failed to generate quiz"
      });
    }
  });

  // Generate quiz on-the-fly (without saving) for fresh explanations
  app.post("/api/quiz/generate", async (req, res) => {
    try {
      const { topic, summary, difficulty } = req.body;
      
      if (!topic || !summary) {
        return res.status(400).json({
          success: false,
          error: "Topic and summary are required"
        });
      }

      console.log(`Generating on-the-fly quiz for topic: ${topic}`);
      
      const quiz = await generateQuiz(
        topic, 
        summary,
        (difficulty as DifficultyLevel) || "age10"
      );

      console.log(`Quiz generated with ${quiz.length} questions`);

      return res.json({
        success: true,
        data: quiz
      });
    } catch (error: any) {
      console.error("Error generating quiz:", error);
      return res.status(500).json({
        success: false,
        error: error.message || "Failed to generate quiz"
      });
    }
  });

  // Get AI-generated topic suggestions
  app.get("/api/topic-suggestions", async (_req, res) => {
    try {
      console.log("Fetching topic suggestions...");
      const suggestions = await generateTopicSuggestions();
      
      return res.json({
        success: true,
        data: suggestions
      });
    } catch (error: any) {
      console.error("Error generating topic suggestions:", error);
      return res.status(500).json({
        success: false,
        error: error.message || "Failed to generate topic suggestions"
      });
    }
  });

  return httpServer;
}
