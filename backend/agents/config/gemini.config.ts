import { GoogleGenerativeAI } from '@google/generative-ai';
import * as dotenv from 'dotenv';

dotenv.config();

/**
 * Gemini AI Configuration for KisaanMitra Agents
 */
export class GeminiConfig {
  private static instance: GoogleGenerativeAI;

  static getInstance(): GoogleGenerativeAI {
    if (!this.instance) {
      const apiKey = process.env.GOOGLE_API_KEY;
      if (!apiKey) {
        throw new Error('GOOGLE_API_KEY not found in environment variables');
      }
      this.instance = new GoogleGenerativeAI(apiKey);
    }
    return this.instance;
  }

  /**
   * Get Gemini model for specific agent tasks
   */
  static getModel(modelName: string = 'gemini-1.5-flash') {
    const genAI = this.getInstance();
    return genAI.getGenerativeModel({ model: modelName });
  }

  /**
   * Agent-specific model configurations
   */
  static readonly MODELS = {
    // Fast model for real-time analysis (Field Intelligence)
    FIELD_INTELLIGENCE: 'gemini-1.5-flash',

    // Pro model for complex economic analysis (Market & Economics)
    MARKET_ECONOMICS: 'gemini-1.5-pro',

    // Flash model for interface/translation tasks
    INTERFACE: 'gemini-1.5-flash',
  };

  /**
   * Generation configs for different tasks
   */
  static readonly GENERATION_CONFIGS = {
    ANALYSIS: {
      temperature: 0.4,
      topP: 0.8,
      topK: 40,
      maxOutputTokens: 2048,
    },
    CREATIVE: {
      temperature: 0.9,
      topP: 0.95,
      topK: 64,
      maxOutputTokens: 1024,
    },
    PRECISE: {
      temperature: 0.2,
      topP: 0.7,
      topK: 20,
      maxOutputTokens: 2048,
    },
  };

  /**
   * Safety settings
   */
  static readonly SAFETY_SETTINGS = [
    {
      category: 'HARM_CATEGORY_HARASSMENT' as any,
      threshold: 'BLOCK_MEDIUM_AND_ABOVE' as any,
    },
    {
      category: 'HARM_CATEGORY_HATE_SPEECH' as any,
      threshold: 'BLOCK_MEDIUM_AND_ABOVE' as any,
    },
  ];
}
