import { type User, type InsertUser, type Explanation, type InsertExplanation, type QuizQuestion, explanations } from "@shared/schema";
import { db } from "./db";
import { eq, desc } from "drizzle-orm";
import { randomUUID } from "crypto";

export interface IStorage {
  getUser(id: string): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  
  saveExplanation(explanation: InsertExplanation): Promise<Explanation>;
  getExplanation(id: number): Promise<Explanation | undefined>;
  getAllExplanations(): Promise<Explanation[]>;
  deleteExplanation(id: number): Promise<boolean>;
  updateExplanationQuiz(id: number, quiz: QuizQuestion[]): Promise<Explanation | undefined>;
}

export class DatabaseStorage implements IStorage {
  private users: Map<string, User>;

  constructor() {
    this.users = new Map();
  }

  async getUser(id: string): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(
      (user) => user.username === username,
    );
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const id = randomUUID();
    const user: User = { ...insertUser, id };
    this.users.set(id, user);
    return user;
  }

  async saveExplanation(insertExplanation: InsertExplanation): Promise<Explanation> {
    const [explanation] = await db
      .insert(explanations)
      .values(insertExplanation)
      .returning();
    return explanation;
  }

  async getExplanation(id: number): Promise<Explanation | undefined> {
    const [explanation] = await db
      .select()
      .from(explanations)
      .where(eq(explanations.id, id));
    return explanation || undefined;
  }

  async getAllExplanations(): Promise<Explanation[]> {
    return await db
      .select()
      .from(explanations)
      .orderBy(desc(explanations.createdAt));
  }

  async deleteExplanation(id: number): Promise<boolean> {
    const result = await db
      .delete(explanations)
      .where(eq(explanations.id, id))
      .returning();
    return result.length > 0;
  }

  async updateExplanationQuiz(id: number, quiz: QuizQuestion[]): Promise<Explanation | undefined> {
    const [updated] = await db
      .update(explanations)
      .set({ quiz })
      .where(eq(explanations.id, id))
      .returning();
    return updated || undefined;
  }
}

export const storage = new DatabaseStorage();
