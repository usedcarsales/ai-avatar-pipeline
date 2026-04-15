// videoRenderer.js — HeyGen CLI-based video generation
// Replaces the old REST API avatarRenderer.js with the official HeyGen CLI

import { execFile } from 'child_process';
import { promisify } from 'util';
import fs from 'fs';
import path from 'path';
import 'dotenv/config';
import { log, error, success, warn } from './utils/logger.js';

const execFileAsync = promisify(execFile);
const HEYGEN_BIN = process.env.HEYGEN_BIN || 'heygen';
const OUTPUT_DIR = process.env.OUTPUT_DIR || './output';

// HeyGen CLI pricing (v3 API, Avatar IV/V)
// Avatar IV: $0.1/sec, Video Agent: $0.0333/sec
const PRICE_PER_SEC = {
  agent: 0.0333,
  avatarIV: 0.1,
  avatarV: 0.1 // pricing TBD, assume same as IV
};

/**
 * Generate a video using HeyGen Video Agent (prompt-to-video)
 * Simplest mode: just describe what you want, HeyGen handles everything
 * @param {string} prompt - Video description/prompt
 * @param {Object} options
 * @param {string} options.avatarId - Specific avatar ID (optional)
 * @param {string} options.voiceId - Specific voice ID (optional)
 * @param {string} options.orientation - 'landscape' | 'portrait' (optional)
 * @param {string} options.styleId - Style template ID (optional)
 * @param {boolean} options.wait - Wait for completion (default: true)
 * @param {number} options.timeout - Max wait time in seconds (default: 1200)
 * @returns {Promise<{videoId: string, videoUrl: string, durationSeconds: number, cost: number}>}
 */
export async function createWithAgent(prompt, options = {}) {
  const {
    avatarId,
    voiceId,
    orientation,
    styleId,
    wait = true,
    timeout = 1200
  } = options;

  log(`🎬 Video Agent: "${prompt.substring(0, 80)}..."`);

  const args = ['video-agent', 'create', '--prompt', prompt];

  if (avatarId) args.push('--avatar-id', avatarId);
  if (voiceId) args.push('--voice-id', voiceId);
  if (orientation) args.push('--orientation', orientation);
  if (styleId) args.push('--style-id', styleId);
  if (wait) {
    args.push('--wait');
    args.push('--timeout', `${timeout}s`);
  }

  try {
    const { stdout } = await execFileAsync(HEYGEN_BIN, args, {
      maxBuffer: 10 * 1024 * 1024 // 10MB buffer for large JSON responses
    });

    const result = JSON.parse(stdout);
    const videoId = result.data?.video_id || result.data?.id;
    const status = result.data?.status;

    if (!wait && status === 'generating') {
      log(`Video generating in background. ID: ${videoId}`);
      return { videoId, status: 'generating' };
    }

    // If --wait, the response should include video_url on completion
    const videoUrl = result.data?.video_url;
    const duration = result.data?.duration || estimateDuration(prompt);
    const cost = estimateCost(duration, 'agent');

    success(`Video ready! ID: ${videoId}`);
    if (videoUrl) success(`URL: ${videoUrl}`);
    success(`Duration: ${duration}s | Estimated cost: $${cost.toFixed(4)}`);

    return {
      videoId,
      videoUrl,
      durationSeconds: duration,
      cost
    };
  } catch (err) {
    error(`HeyGen CLI video-agent failed: ${err.message}`);
    throw err;
  }
}

/**
 * Create a video with specific avatar and script
 * For when you want full control over avatar, script, and voice
 * @param {Object} params
 * @param {string} params.avatarId - HeyGen avatar ID
 * @param {string} params.script - Script text for the avatar to speak
 * @param {string} params.voiceId - HeyGen voice ID
 * @param {string} params.type - 'avatar' or 'image' (default: 'avatar')
 * @param {Object} params.image - For type='image': {type: 'url', url: '...'}
 * @param {boolean} params.wait - Wait for completion (default: true)
 * @param {number} params.timeout - Max wait in seconds (default: 1200)
 * @returns {Promise<{videoId, videoUrl, durationSeconds, cost}>}
 */
export async function createWithAvatar(params = {}) {
  const {
    avatarId,
    script,
    voiceId,
    type = 'avatar',
    image,
    wait = true,
    timeout = 1200
  } = params;

  if (!script) throw new Error('script is required');
  if (!avatarId && type === 'avatar') throw new Error('avatarId is required for avatar type');
  if (!voiceId) throw new Error('voiceId is required');

  log(`🎬 Avatar video: avatar=${avatarId || 'custom'}, script="${script.substring(0, 50)}..."`);

  const body = { type, script, voice_id: voiceId };
  if (avatarId) body.avatar_id = avatarId;
  if (image) body.image = image;

  const args = ['video', 'create', '-d', JSON.stringify(body)];

  if (wait) {
    args.push('--wait');
    args.push('--timeout', `${timeout}s`);
  }

  try {
    const { stdout } = await execFileAsync(HEYGEN_BIN, args, {
      maxBuffer: 10 * 1024 * 1024
    });

    const result = JSON.parse(stdout);
    const videoId = result.data?.id || result.data?.video_id;
    const videoUrl = result.data?.video_url;
    const duration = result.data?.duration || estimateDuration(script);
    const cost = estimateCost(duration, 'avatarIV');

    success(`Avatar video ready! ID: ${videoId}`);
    if (videoUrl) success(`URL: ${videoUrl}`);
    success(`Duration: ${duration}s | Estimated cost: $${cost.toFixed(4)}`);

    return { videoId, videoUrl, durationSeconds: duration, cost };
  } catch (err) {
    error(`HeyGen CLI video create failed: ${err.message}`);
    throw err;
  }
}

/**
 * Download a completed video
 * @param {string} videoId - HeyGen video ID
 * @param {string} outputFilename - Local filename (default: auto-generated)
 * @param {Object} options
 * @param {'video'|'captioned'} options.asset - Download video or captioned version
 * @returns {Promise<{path: string}>}
 */
export async function downloadVideo(videoId, outputFilename, options = {}) {
  const { asset = 'video' } = options;

  const videoDir = path.join(OUTPUT_DIR, 'videos');
  fs.mkdirSync(videoDir, { recursive: true });

  const outputPath = path.join(videoDir, outputFilename || `${videoId}.mp4`);

  log(`Downloading video ${videoId}...`);

  const args = ['video', 'download', videoId, '--output-path', outputPath];
  if (asset === 'captioned') args.push('--asset', 'captioned');

  try {
    const { stdout } = await execFileAsync(HEYGEN_BIN, args);
    const result = JSON.parse(stdout);

    success(`Video downloaded: ${outputPath}`);
    return { path: outputPath };
  } catch (err) {
    error(`Download failed: ${err.message}`);
    throw err;
  }
}

/**
 * Check video status
 * @param {string} videoId
 * @returns {Promise<Object>} Video status object
 */
export async function getVideoStatus(videoId) {
  const { stdout } = await execFileAsync(HEYGEN_BIN, ['video', 'get', videoId]);
  const result = JSON.parse(stdout);
  return result.data;
}

/**
 * List available avatars
 * @param {Object} options
 * @param {'public'|'private'} options.ownership - Filter by ownership
 * @param {number} options.limit - Max results (default: 50)
 * @returns {Promise<Array>} Array of avatar objects
 */
export async function listAvatars(options = {}) {
  const { ownership, limit = 50 } = options;

  const args = ['avatar', 'list', '--limit', String(limit), '--human'];
  if (ownership) args.push('--ownership', ownership);

  const { stdout } = await execFileAsync(HEYGEN_BIN, args);
  // --human outputs a table, --json outputs structured data
  // Use without --human for programmatic access
  const argsJson = ['avatar', 'list', '--limit', String(limit)];
  if (ownership) argsJson.push('--ownership', ownership);

  const { stdout: jsonOutput } = await execFileAsync(HEYGEN_BIN, argsJson);
  const result = JSON.parse(jsonOutput);

  log(`Found ${result.data?.length || 0} avatars`);
  return result.data || [];
}

/**
 * Estimate cost for a video
 * @param {number} durationSeconds
 * @param {'agent'|'avatarIV'|'avatarV'} mode
 * @returns {number} Estimated cost in USD
 */
export function estimateCost(durationSeconds, mode = 'agent') {
  return durationSeconds * (PRICE_PER_SEC[mode] || PRICE_PER_SEC.agent);
}

/**
 * Rough duration estimate from word count
 * @param {string} text
 * @returns {number} Estimated seconds
 */
function estimateDuration(text) {
  const wordCount = text.split(/\s+/).length;
  return Math.round(wordCount / 2.5); // ~150 words/min
}

/**
 * Authenticate with HeyGen CLI
 * @param {string} apiKey - HeyGen API key
 * @returns {Promise<boolean>} Success status
 */
export async function authenticate(apiKey) {
  if (!apiKey) {
    // Try env var
    apiKey = process.env.HEYGEN_API_KEY;
  }

  if (apiKey) {
    // Set via environment variable (preferred for automation)
    log('HEYGEN_API_KEY set via environment');
    return true;
  }

  // Check if already authenticated
  try {
    await execFileAsync(HEYGEN_BIN, ['auth', 'status']);
    success('HeyGen CLI already authenticated');
    return true;
  } catch {
    warn('HeyGen CLI not authenticated. Run: heygen auth login');
    return false;
  }
}

export default {
  createWithAgent,
  createWithAvatar,
  downloadVideo,
  getVideoStatus,
  listAvatars,
  estimateCost,
  authenticate
};