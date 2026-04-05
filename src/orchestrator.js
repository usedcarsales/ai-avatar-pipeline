// orchestrator.js — Main AI Avatar Video Pipeline runner

import 'dotenv/config';
import { generateScript } from './scriptGenerator.js';
import { synthesize } from './voiceSynth.js';
import { render, estimateCost } from './avatarRenderer.js';
import { log, success, warn } from './utils/logger.js';

/**
 * Run the full video production pipeline
 * @param {string} topic - Video topic or full script text
 * @param {Object} options
 * @param {string} options.avatarId - HeyGen avatar ID (required)
 * @param {string} options.voiceId - Fish Audio voice ID (required)
 * @param {'short'|'medium'|'long'} options.length - Script length
 * @param {'professional'|'casual'|'educational'} options.style - Speaking style
 * @param {string} options.targetAudience - Target viewer demographic
 * @param {'III'|'IV'} options.engine - HeyGen engine version (default: III)
 * @returns {Promise<{videoId, videoUrl, script, audioPath, durationSeconds, cost}>}
 */
export async function runPipeline(topic, options = {}) {
  const {
    avatarId = process.env.DEFAULT_AVATAR_ID,
    voiceId = process.env.DEFAULT_VOICE_ID,
    length = 'medium',
    style = 'professional',
    targetAudience = 'business professionals',
    engine = 'III'
  } = options;

  if (!avatarId) {
    throw new Error('avatarId is required. Set DEFAULT_AVATAR_ID in .env or pass via options.');
  }
  if (!voiceId) {
    throw new Error('voiceId is required. Set DEFAULT_VOICE_ID in .env or pass via options.');
  }

  log(`🎬 Pipeline starting for: "${topic}"`);
  const startTime = Date.now();

  // Step 1: Generate script
  log('Step 1/3: Generating script...');
  const scriptResult = await generateScript(topic, { length, style, targetAudience });
  log(`Script: "${scriptResult.title}" (~${scriptResult.estimatedDuration}s)`);

  // Step 2: Synthesize voice
  log('Step 2/3: Synthesizing voice...');
  const audioPath = await synthesize(scriptResult.script, voiceId);

  // Step 3: Render avatar video
  log('Step 3/3: Rendering avatar video...');
  const videoResult = await render(scriptResult.script, avatarId, { engine });

  const totalTime = ((Date.now() - startTime) / 1000).toFixed(1);
  success(`Pipeline complete in ${totalTime}s`);
  success(`Video URL: ${videoResult.videoUrl}`);
  success(`Total cost: $${videoResult.cost.toFixed(4)}`);

  return {
    videoId: videoResult.videoId,
    videoUrl: videoResult.videoUrl,
    script: scriptResult,
    audioPath,
    durationSeconds: videoResult.durationSeconds,
    cost: videoResult.cost
  };
}

// Run from CLI: node src/orchestrator.js "Your topic here"
const isMain = process.argv[1]?.endsWith('orchestrator.js');
if (isMain) {
  const topic = process.argv[2];
  if (!topic) {
    console.error('Usage: node src/orchestrator.js "Your video topic"');
    process.exit(1);
  }

  const avatarId = process.env.DEFAULT_AVATAR_ID;
  const voiceId = process.env.DEFAULT_VOICE_ID;

  if (!avatarId || !voiceId) {
    warn('DEFAULT_AVATAR_ID or DEFAULT_VOICE_ID not set in .env');
    warn('Run `node -e "import(\'./src/avatarRenderer.js\').then(m => m.listAvatars().then(console.log))"` to find avatar IDs');
    warn('Run `node -e "import(\'./src/voiceSynth.js\').then(m => m.listVoices().then(console.log))"` to find voice IDs');
    process.exit(1);
  }

  runPipeline(topic)
    .then(result => {
      console.log('\n📊 Pipeline Result:');
      console.log(JSON.stringify(result, null, 2));
    })
    .catch(err => {
      console.error('Pipeline failed:', err.message);
      process.exit(1);
    });
}

export default { runPipeline };
