import OpenAI from "openai";
import pLimit from "p-limit";
import pRetry from "p-retry";
import type { DifficultyLevel } from "@shared/schema";

// the newest OpenAI model is "gpt-5" which was released August 7, 2025. do not change this unless explicitly requested by the user
// This is using Replit's AI Integrations service, which provides OpenAI-compatible API access without requiring your own OpenAI API key.
const openai = new OpenAI({
  baseURL: process.env.AI_INTEGRATIONS_OPENAI_BASE_URL,
  apiKey: process.env.AI_INTEGRATIONS_OPENAI_API_KEY
});

function isRateLimitError(error: any): boolean {
  const errorMsg = error?.message || String(error);
  return (
    errorMsg.includes("429") ||
    errorMsg.includes("RATELIMIT_EXCEEDED") ||
    errorMsg.toLowerCase().includes("quota") ||
    errorMsg.toLowerCase().includes("rate limit")
  );
}

export interface ExplanationContent {
  topic: string;
  simpleSummary: string;
  comicPanels: {
    id: number;
    title: string;
    description: string;
    speechBubble: string;
    imagePrompt: string;
  }[];
  illustrations: {
    id: number;
    title: string;
    description: string;
    imagePrompt: string;
  }[];
  slides: {
    id: number;
    title: string;
    content: string;
    narration: string;
    imagePrompt: string;
  }[];
}

export async function analyzeImageTopic(imageBase64: string): Promise<string> {
  const response = await pRetry(
    async () => {
      const result = await openai.chat.completions.create({
        model: "gpt-4o", // Using GPT-4o which is available via Replit AI Integrations
        messages: [
          {
            role: "system",
            content: "You are an expert at analyzing images and identifying the main topic or concept being shown. Respond with a clear, concise description of the main topic or concept in the image that could be explained to someone."
          },
          {
            role: "user",
            content: [
              {
                type: "image_url",
                image_url: { url: imageBase64 }
              },
              {
                type: "text",
                text: "What is the main topic or concept shown in this image? Provide a clear topic statement that could be used to generate an educational explanation."
              }
            ]
          }
        ],
        max_completion_tokens: 500
      });
      return result.choices[0]?.message?.content || "Unknown topic";
    },
    {
      retries: 3,
      minTimeout: 2000,
      factor: 2,
      onFailedAttempt: (error) => {
        if (!isRateLimitError(error)) {
          throw error;
        }
      }
    }
  );
  
  return response;
}

function getDifficultyPrompt(difficulty: DifficultyLevel): { audience: string; style: string; complexity: string } {
  switch (difficulty) {
    case "age5":
      return {
        audience: "a curious 5-year-old child",
        style: "Use very simple words, fun comparisons to toys and everyday things, and lots of imagination. Keep sentences very short.",
        complexity: "Very simple concepts only. Use analogies like 'it's like when you play with blocks' or 'imagine your favorite superhero'."
      };
    case "age10":
      return {
        audience: "a bright 10-year-old student",
        style: "Use clear, engaging language with some scientific terms explained simply. Include interesting facts and 'did you know' moments.",
        complexity: "Moderate complexity. Can include basic scientific concepts, cause-and-effect relationships, and step-by-step processes."
      };
    case "adult":
      return {
        audience: "an adult beginner who wants to understand the topic properly",
        style: "Use clear, professional language. Include proper terminology with explanations. Be comprehensive but accessible.",
        complexity: "Full complexity. Include technical details, real-world applications, and nuanced explanations."
      };
    default:
      return getDifficultyPrompt("age10");
  }
}

export async function generateExplanation(topic: string, difficulty: DifficultyLevel = "age10"): Promise<ExplanationContent> {
  const difficultyGuide = getDifficultyPrompt(difficulty);
  
  const response = await pRetry(
    async () => {
      const result = await openai.chat.completions.create({
        model: "gpt-4o", // Using GPT-4o which is available via Replit AI Integrations
        messages: [
          {
            role: "system",
            content: `You are an expert educator who explains complex topics for ${difficultyGuide.audience}. ${difficultyGuide.style} ${difficultyGuide.complexity}

You create engaging educational content with comics, illustrations, and slideshows. Output valid JSON only.`
          },
          {
            role: "user",
            content: `Create a fun, engaging explanation of this topic: "${topic}"
            
Target audience: ${difficultyGuide.audience}

Generate a JSON response with this exact structure:
{
  "topic": "The topic title (short, engaging)",
  "simpleSummary": "A 2-3 sentence explanation appropriate for the target audience",
  "comicPanels": [
    {
      "id": 1,
      "title": "Panel title",
      "description": "What happens in this panel",
      "speechBubble": "Fun dialogue or narration for the speech bubble",
      "imagePrompt": "Detailed prompt for generating a child-friendly, colorful illustration for this panel"
    }
  ],
  "illustrations": [
    {
      "id": 1,
      "title": "Illustration title",
      "description": "What this illustration shows",
      "imagePrompt": "Detailed prompt for generating a clear, educational illustration"
    }
  ],
  "slides": [
    {
      "id": 1,
      "title": "Slide title",
      "content": "Main content for this slide (1-2 sentences)",
      "narration": "What to say when presenting this slide (conversational, friendly)",
      "imagePrompt": "Detailed prompt for generating a visual for this slide"
    }
  ]
}

Create 10 comic panels, 6 illustrations, and 8 slides. Adjust complexity for the target audience. The image prompts should describe colorful educational illustrations appropriate for the audience.`
          }
        ],
        response_format: { type: "json_object" },
        max_completion_tokens: 8000
      });
      
      const content = result.choices[0]?.message?.content;
      if (!content) {
        console.error("OpenAI response:", JSON.stringify(result, null, 2));
        throw new Error("No content generated - API returned empty response");
      }
      
      try {
        return JSON.parse(content) as ExplanationContent;
      } catch (parseError) {
        console.error("Failed to parse JSON:", content);
        throw new Error("Invalid JSON response from API");
      }
    },
    {
      retries: 3,
      minTimeout: 2000,
      factor: 2,
      onFailedAttempt: (context) => {
        const errorMsg = context.error?.message || String(context.error);
        console.log(`Text generation attempt failed: ${errorMsg}, retries left: ${context.retriesLeft}`);
        if (!isRateLimitError(context.error)) {
          throw context.error;
        }
      }
    }
  );
  
  return response;
}

export async function generateImage(prompt: string): Promise<string> {
  const enhancedPrompt = `Create a child-friendly, colorful, cartoon-style educational illustration: ${prompt}. Style: bright colors, simple shapes, friendly characters, suitable for children, no text in image.`;
  
  const response = await pRetry(
    async () => {
      const result = await openai.images.generate({
        model: "gpt-image-1",
        prompt: enhancedPrompt,
        size: "1024x1024",
      });
      
      const base64 = result.data?.[0]?.b64_json;
      if (!base64) {
        throw new Error("Image generation failed: no base64 data returned");
      }
      return `data:image/png;base64,${base64}`;
    },
    {
      retries: 5,
      minTimeout: 3000,
      maxTimeout: 30000,
      factor: 2,
      onFailedAttempt: (context) => {
        const errorMessage = context.error?.message || String(context.error);
        console.log(`Image generation attempt failed: ${errorMessage}`);
        if (!isRateLimitError(context.error) && !errorMessage.includes("timeout")) {
          throw context.error;
        }
      }
    }
  );
  
  return response;
}

export async function generateAllImages(
  prompts: { id: number; prompt: string; type: "comic" | "illustration" | "slide" }[]
): Promise<Map<string, string>> {
  const limit = pLimit(2); // Process 2 images at a time to avoid rate limits
  const results = new Map<string, string>();
  
  const tasks = prompts.map(({ id, prompt, type }) =>
    limit(async () => {
      try {
        const imageBase64 = await generateImage(prompt);
        results.set(`${type}-${id}`, imageBase64);
      } catch (error) {
        console.error(`Failed to generate image for ${type}-${id}:`, error);
        // Continue without image if generation fails
      }
    })
  );
  
  await Promise.all(tasks);
  return results;
}

export interface QuizQuestion {
  id: number;
  question: string;
  options: string[];
  correctIndex: number;
  explanation: string;
}

export interface TopicSuggestion {
  topic: string;
  description: string;
  category: string;
}

export async function generateTopicSuggestions(): Promise<TopicSuggestion[]> {
  console.log("Generating topic suggestions...");
  
  const response = await pRetry(
    async () => {
      const result = await openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
          {
            role: "system",
            content: `You are an expert educator who suggests interesting, engaging educational topics for learners of all ages. Generate diverse topics across different categories like science, history, technology, nature, and everyday life. You MUST output valid JSON only.`
          },
          {
            role: "user",
            content: `Generate 8 interesting educational topic suggestions that would be fun to learn about. Include a mix of:
- Science & Nature topics (how things work, animals, space, etc.)
- Technology & Innovation topics (computers, internet, inventions)
- History & Culture topics (historical events, cultures, discoveries)
- Everyday Life topics (how everyday objects work, health, food)

Generate a JSON response with this exact structure:
{
  "suggestions": [
    {
      "topic": "A clear, engaging topic question or statement",
      "description": "A one-sentence hook that makes the topic interesting",
      "category": "Science" | "Technology" | "History" | "Nature" | "Everyday"
    }
  ]
}

Make topics interesting and appropriate for all ages. Each topic should spark curiosity!

Return ONLY the JSON object, no other text.`
          }
        ],
        response_format: { type: "json_object" },
        max_tokens: 1500
      });
      
      const content = result.choices[0]?.message?.content;
      if (!content) {
        throw new Error("No suggestions generated");
      }
      
      const parsed = JSON.parse(content) as { suggestions: TopicSuggestion[] };
      
      if (!parsed.suggestions || !Array.isArray(parsed.suggestions) || parsed.suggestions.length === 0) {
        throw new Error("Invalid suggestions structure");
      }
      
      console.log(`Generated ${parsed.suggestions.length} topic suggestions`);
      return parsed.suggestions;
    },
    {
      retries: 3,
      minTimeout: 2000,
      factor: 2,
      onFailedAttempt: (context) => {
        const errorMsg = context.error?.message || String(context.error);
        console.log(`Topic suggestions generation attempt failed: ${errorMsg}. Retrying...`);
      }
    }
  );
  
  return response;
}

export async function generateQuiz(topic: string, summary: string, difficulty: DifficultyLevel = "age10"): Promise<QuizQuestion[]> {
  const difficultyGuide = getDifficultyPrompt(difficulty);
  
  console.log(`Starting quiz generation for topic: ${topic}`);
  
  const response = await pRetry(
    async () => {
      console.log("Calling OpenAI for quiz generation...");
      const result = await openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
          {
            role: "system",
            content: `You are an expert educator creating quiz questions for ${difficultyGuide.audience}. ${difficultyGuide.style}

Create engaging, educational quiz questions that test understanding of the topic. You MUST output valid JSON only.`
          },
          {
            role: "user",
            content: `Create a fun quiz about this topic: "${topic}"

Topic Summary: ${summary}

Target audience: ${difficultyGuide.audience}

Generate a JSON response with this exact structure:
{
  "questions": [
    {
      "id": 1,
      "question": "A clear, engaging question about the topic",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correctIndex": 0,
      "explanation": "A brief explanation of why this is the correct answer"
    }
  ]
}

Create 5 multiple-choice questions with 4 options each. Make sure:
- Questions are appropriate for the target audience
- Questions test understanding, not just memorization
- Explanations are helpful and educational
- The correct answer index (0-3) is accurate

Return ONLY the JSON object, no other text.`
          }
        ],
        response_format: { type: "json_object" },
        max_tokens: 2000
      });
      
      console.log("OpenAI response received:", result.choices[0]?.finish_reason);
      
      const content = result.choices[0]?.message?.content;
      if (!content) {
        console.error("No content in OpenAI response");
        throw new Error("No quiz content generated - empty response from AI");
      }
      
      console.log("Parsing quiz content...");
      const parsed = JSON.parse(content) as { questions: QuizQuestion[] };
      
      if (!parsed.questions || !Array.isArray(parsed.questions) || parsed.questions.length === 0) {
        console.error("Invalid quiz structure:", parsed);
        throw new Error("Invalid quiz structure - no questions array");
      }
      
      console.log(`Successfully generated ${parsed.questions.length} quiz questions`);
      return parsed.questions;
    },
    {
      retries: 5,
      minTimeout: 3000,
      maxTimeout: 30000,
      factor: 2,
      onFailedAttempt: (context) => {
        const errorMsg = context.error?.message || String(context.error);
        console.log(`Quiz generation attempt failed: ${errorMsg}. Retrying...`);
      }
    }
  );
  
  return response;
}
