// scriptGenerator.js — LLM-powered video script generation using Claude

import 'dotenv/config';
import { log, error } from './utils/logger.js';

const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;
const MODEL = 'claude-3-5-haiku-20241022'; // Cost-efficient for script gen

const LENGTH_TARGETS = {
  short: { words: 150, seconds: 60 },
  medium: { words: 300, seconds: 120 },
  long: { words: 600, seconds: 240 }
};

/**
 * Generate a video script for a given topic
 * @param {string} topic - The video topic
 * @param {Object} options
 * @param {'short'|'medium'|'long'} options.length - Target video length
 * @param {'professional'|'casual'|'educational'} options.style - Speaking style
 * @param {string} options.targetAudience - Who the video is for
 * @returns {Promise<{title: string, script: string, estimatedDuration: number}>}
 */
export async function generateScript(topic, options = {}) {
  const {
    length = 'medium',
    style = 'professional',
    targetAudience = 'business professionals'
  } = options;

  const target = LENGTH_TARGETS[length];

  log(`Generating ${length} ${style} script for: "${topic}"`);

  const systemPrompt = `You are a professional video scriptwriter specializing in AI avatar content. 
Write compelling, tight scripts that work perfectly when spoken aloud by an AI avatar presenter.
Rules:
- No stage directions, no [pause], no (smiles) — just the spoken words
- No introductions like "Hi, I'm [name]" unless specifically requested
- Hook the viewer in the first sentence
- Keep sentences short and punchy — easy to follow when spoken
- End with a clear call to action
- Target exactly ${target.words} words (approximately ${target.seconds} seconds when spoken)`;

  const userPrompt = `Write a ${style} video script about: "${topic}"
Target audience: ${targetAudience}
Style: ${style}
Approximate length: ${target.words} words

Return a JSON object with:
- title: a compelling video title (max 60 chars, good for YouTube SEO)
- script: the full script text (spoken words only, no directions)
- estimatedDuration: estimated seconds to speak at normal pace`;

  if (!ANTHROPIC_API_KEY) {
    throw new Error('ANTHROPIC_API_KEY not set in .env');
  }

  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'x-api-key': ANTHROPIC_API_KEY,
      'anthropic-version': '2023-06-01',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: MODEL,
      max_tokens: 1024,
      system: systemPrompt,
      messages: [{ role: 'user', content: userPrompt }]
    })
  });

  if (!response.ok) {
    const err = await response.text();
    error(`Anthropic API error: ${response.status} ${err}`);
    throw new Error(`Script generation failed: ${response.status}`);
  }

  const data = await response.json();
  const content = data.content[0].text;

  // Parse JSON from response
  const jsonMatch = content.match(/\{[\s\S]*\}/);
  if (!jsonMatch) {
    throw new Error('Could not parse JSON from script generator response');
  }

  const result = JSON.parse(jsonMatch[0]);
  log(`Script generated: "${result.title}" (~${result.estimatedDuration}s)`);
  return result;
}

export default { generateScript };
