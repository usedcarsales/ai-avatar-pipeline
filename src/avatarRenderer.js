// avatarRenderer.js — HeyGen API integration for avatar video generation

import 'dotenv/config';
import { log, error, success, warn } from './utils/logger.js';

const HEYGEN_API_KEY = process.env.HEYGEN_API_KEY;

// HeyGen Engine III pricing: $0.0167/sec
const PRICE_PER_SEC = {
  III: 0.0167,
  IV: 0.1
};

const POLL_INTERVAL_MS = 5000;
const MAX_POLL_ATTEMPTS = 120; // 10 minutes max wait

/**
 * Render an avatar video using HeyGen API
 * @param {string} scriptText - The script to speak
 * @param {string} avatarId - HeyGen avatar ID
 * @param {Object} options
 * @param {string} options.engine - 'III' or 'IV' (default: 'III')
 * @param {number} options.width - Video width (default: 1280)
 * @param {number} options.height - Video height (default: 720)
 * @returns {Promise<{videoId: string, videoUrl: string, durationSeconds: number, cost: number}>}
 */
export async function render(scriptText, avatarId, options = {}) {
  const {
    engine = 'III',
    width = 1280,
    height = 720
  } = options;

  if (!HEYGEN_API_KEY) {
    throw new Error('HEYGEN_API_KEY not set in .env');
  }

  if (!avatarId) {
    throw new Error('avatarId is required for HeyGen rendering');
  }

  log(`Rendering avatar video with avatar: ${avatarId} (Engine ${engine})`);

  // Submit render job
  const submitResponse = await fetch('https://api.heygen.com/v1/video/generate', {
    method: 'POST',
    headers: {
      'X-API-KEY': HEYGEN_API_KEY,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      video_inputs: [{
        character: {
          type: 'avatar',
          avatar_id: avatarId
        },
        voice: {
          type: 'text',
          input_text: scriptText
        }
      }],
      dimension: { width, height },
      use_avatar_iv_model: engine === 'IV'
    })
  });

  if (!submitResponse.ok) {
    const err = await submitResponse.text();
    error(`HeyGen submit error: ${submitResponse.status} ${err}`);
    throw new Error(`Video render submission failed: ${submitResponse.status}`);
  }

  const submitData = await submitResponse.json();
  const videoId = submitData.data?.video_id;

  if (!videoId) {
    throw new Error(`HeyGen did not return a video_id: ${JSON.stringify(submitData)}`);
  }

  log(`Render job submitted. video_id: ${videoId} — polling for completion...`);

  // Poll for completion
  let attempts = 0;
  while (attempts < MAX_POLL_ATTEMPTS) {
    await sleep(POLL_INTERVAL_MS);
    attempts++;

    const pollResponse = await fetch(
      `https://api.heygen.com/v1/video_status.get?video_id=${videoId}`,
      { headers: { 'X-API-KEY': HEYGEN_API_KEY } }
    );

    if (!pollResponse.ok) {
      warn(`Poll attempt ${attempts} failed: ${pollResponse.status}`);
      continue;
    }

    const pollData = await pollResponse.json();
    const status = pollData.data?.status;
    const elapsed = (attempts * POLL_INTERVAL_MS / 1000).toFixed(0);

    log(`Status: ${status} (${elapsed}s elapsed)`);

    if (status === 'completed') {
      const videoUrl = pollData.data.video_url;
      const durationSeconds = pollData.data.duration || estimateDuration(scriptText);
      const cost = estimateCost(durationSeconds, engine);

      success(`Video ready! URL: ${videoUrl}`);
      success(`Duration: ${durationSeconds}s | Estimated cost: $${cost.toFixed(4)}`);

      return { videoId, videoUrl, durationSeconds, cost };
    }

    if (status === 'failed') {
      const reason = pollData.data?.error || 'Unknown error';
      error(`Render failed: ${reason}`);
      throw new Error(`HeyGen render failed: ${reason}`);
    }
  }

  throw new Error(`Render timed out after ${MAX_POLL_ATTEMPTS} poll attempts`);
}

/**
 * List available avatars from HeyGen
 * @returns {Promise<Array>} Array of avatar objects
 */
export async function listAvatars() {
  if (!HEYGEN_API_KEY) {
    throw new Error('HEYGEN_API_KEY not set in .env');
  }

  log('Fetching available HeyGen avatars...');

  const response = await fetch('https://api.heygen.com/v2/avatars', {
    headers: { 'X-API-KEY': HEYGEN_API_KEY }
  });

  if (!response.ok) {
    const err = await response.text();
    error(`HeyGen list avatars error: ${response.status} ${err}`);
    throw new Error(`Failed to list avatars: ${response.status}`);
  }

  const data = await response.json();
  const avatars = data.data?.avatars || [];
  log(`Found ${avatars.length} avatars`);
  return avatars;
}

/**
 * Estimate cost for a video of given duration
 * @param {number} durationSeconds
 * @param {'III'|'IV'} engine
 * @returns {number} Estimated cost in USD
 */
export function estimateCost(durationSeconds, engine = 'III') {
  return durationSeconds * PRICE_PER_SEC[engine];
}

/**
 * Rough estimate of audio duration from word count
 * @param {string} text
 * @returns {number} Estimated seconds
 */
function estimateDuration(text) {
  const wordCount = text.split(/\s+/).length;
  return Math.round(wordCount / 2.5); // ~150 words/min
}

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

export default { render, listAvatars, estimateCost };
