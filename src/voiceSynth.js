// voiceSynth.js — Fish Audio TTS integration

import 'dotenv/config';
import fs from 'fs';
import path from 'path';
import { log, error, success } from './utils/logger.js';

const FISH_AUDIO_API_KEY = process.env.FISH_AUDIO_API_KEY;
const OUTPUT_DIR = process.env.OUTPUT_DIR || './output';

/**
 * Synthesize text to speech using Fish Audio
 * @param {string} text - The script text to synthesize
 * @param {string} voiceId - Fish Audio voice/model reference ID
 * @param {Object} options
 * @param {'mp3'|'wav'|'pcm'} options.format - Output audio format
 * @param {number} options.bitrate - MP3 bitrate (default 128)
 * @returns {Promise<string>} Path to the saved audio file
 */
export async function synthesize(text, voiceId, options = {}) {
  const {
    format = 'mp3',
    bitrate = 128
  } = options;

  if (!FISH_AUDIO_API_KEY) {
    throw new Error('FISH_AUDIO_API_KEY not set in .env');
  }

  if (!voiceId) {
    throw new Error('voiceId is required for Fish Audio synthesis');
  }

  log(`Synthesizing ${text.length} chars with voice: ${voiceId}`);

  const response = await fetch('https://api.fish.audio/v1/tts', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${FISH_AUDIO_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      text,
      reference_id: voiceId,
      format,
      mp3_bitrate: bitrate
    })
  });

  if (!response.ok) {
    const err = await response.text();
    error(`Fish Audio API error: ${response.status} ${err}`);
    throw new Error(`Voice synthesis failed: ${response.status}`);
  }

  // Save audio to file
  const audioDir = path.join(OUTPUT_DIR, 'audio');
  fs.mkdirSync(audioDir, { recursive: true });

  const timestamp = Date.now();
  const audioPath = path.join(audioDir, `${timestamp}.${format}`);

  const buffer = await response.arrayBuffer();
  fs.writeFileSync(audioPath, Buffer.from(buffer));

  const fileSizeKB = Math.round(fs.statSync(audioPath).size / 1024);
  success(`Audio saved: ${audioPath} (${fileSizeKB}KB)`);

  return audioPath;
}

/**
 * List available voices from Fish Audio
 * @returns {Promise<Array>} Array of voice model objects
 */
export async function listVoices() {
  if (!FISH_AUDIO_API_KEY) {
    throw new Error('FISH_AUDIO_API_KEY not set in .env');
  }

  log('Fetching available Fish Audio voices...');

  const response = await fetch('https://api.fish.audio/v1/model?page_size=20', {
    headers: {
      'Authorization': `Bearer ${FISH_AUDIO_API_KEY}`
    }
  });

  if (!response.ok) {
    const err = await response.text();
    error(`Fish Audio list voices error: ${response.status} ${err}`);
    throw new Error(`Failed to list voices: ${response.status}`);
  }

  const data = await response.json();
  log(`Found ${data.items?.length || 0} voices`);
  return data.items || [];
}

export default { synthesize, listVoices };
