// orchestrator.js — AI Avatar Video Pipeline (v2 — HeyGen CLI architecture)
// Replaces old REST-based pipeline with HeyGen CLI-first approach

import 'dotenv/config';
import { generateScript } from './scriptGenerator.js';
import { createWithAgent, createWithAvatar, downloadVideo, authenticate, listAvatars } from './videoRenderer.js';
import { log, success, warn, error } from './utils/logger.js';
import fs from 'fs';
import path from 'path';

const OUTPUT_DIR = process.env.OUTPUT_DIR || './output';

/**
 * Run the full video production pipeline using HeyGen Video Agent
 * Simplest mode: just provide a topic, HeyGen handles script + avatar + voice
 * @param {string} topic - Video topic or description
 * @param {Object} options
 * @param {string} options.avatarId - Specific avatar (optional, agent picks one)
 * @param {string} options.voiceId - Specific voice (optional, agent picks one)
 * @param {'landscape'|'portrait'} options.orientation - Video orientation
 * @param {boolean} options.download - Download the video file (default: true)
 * @param {boolean} options.useScript - Generate script with Claude first (default: true)
 * @param {'short'|'medium'|'long'} options.length - Script length
 * @param {'professional'|'casual'|'educational'} options.style - Script style
 * @returns {Promise<{videoId, videoUrl, script, durationSeconds, cost, localPath}>}
 */
export async function runPipeline(topic, options = {}) {
  const {
    avatarId,
    voiceId,
    orientation = 'landscape',
    download = true,
    useScript = true,
    length = 'medium',
    style = 'professional'
  } = options;

  log(`🎬 Pipeline starting for: "${topic}"`);
  const startTime = Date.now();

  // Step 1: Generate or use provided script
  let prompt;
  if (useScript) {
    log('Step 1/3: Generating script with Claude...');
    const scriptResult = await generateScript(topic, { length, style });
    prompt = scriptResult.script;
    log(`Script: "${scriptResult.title}" (~${scriptResult.estimatedDuration}s)`);
  } else {
    log('Step 1/3: Using raw topic as prompt (Video Agent will auto-script)');
    prompt = topic;
  }

  // Step 2: Generate video with HeyGen Video Agent
  log('Step 2/3: Generating video with HeyGen...');
  const videoResult = await createWithAgent(prompt, {
    avatarId,
    voiceId,
    orientation,
    wait: true
  });

  // Step 3: Download video
  let localPath = null;
  if (download && videoResult.videoId) {
    log('Step 3/3: Downloading video...');
    const filename = `${videoResult.videoId}.mp4`;
    const downloadResult = await downloadVideo(videoResult.videoId, filename);
    localPath = downloadResult.path;
  } else {
    log('Step 3/3: Skipping download (video available at URL)');
  }

  const totalTime = ((Date.now() - startTime) / 1000).toFixed(1);
  success(`Pipeline complete in ${totalTime}s`);
  success(`Video ID: ${videoResult.videoId}`);
  if (videoResult.videoUrl) success(`Video URL: ${videoResult.videoUrl}`);
  if (localPath) success(`Local file: ${localPath}`);
  success(`Estimated cost: $${videoResult.cost.toFixed(4)}`);

  return {
    videoId: videoResult.videoId,
    videoUrl: videoResult.videoUrl,
    durationSeconds: videoResult.durationSeconds,
    cost: videoResult.cost,
    localPath,
    totalTime: parseFloat(totalTime)
  };
}

/**
 * Run pipeline with specific avatar and voice (full control mode)
 * For when you want exact avatar/voice matching for brand consistency
 * @param {string} script - Pre-written script text
 * @param {string} avatarId - HeyGen avatar ID
 * @param {string} voiceId - HeyGen voice ID
 * @param {Object} options
 * @returns {Promise<Object>} Same as runPipeline
 */
export async function runPipelineWithAvatar(script, avatarId, voiceId, options = {}) {
  const { download = true } = options;

  log(`🎬 Avatar Pipeline: avatar=${avatarId}, voice=${voiceId}`);
  const startTime = Date.now();

  const videoResult = await createWithAvatar({
    avatarId,
    script,
    voiceId,
    wait: true
  });

  let localPath = null;
  if (download && videoResult.videoId) {
    const filename = `${videoResult.videoId}.mp4`;
    const downloadResult = await downloadVideo(videoResult.videoId, filename);
    localPath = downloadResult.path;
  }

  const totalTime = ((Date.now() - startTime) / 1000).toFixed(1);
  success(`Avatar pipeline complete in ${totalTime}s`);

  return {
    videoId: videoResult.videoId,
    videoUrl: videoResult.videoUrl,
    durationSeconds: videoResult.durationSeconds,
    cost: videoResult.cost,
    localPath,
    totalTime: parseFloat(totalTime)
  };
}

/**
 * Batch produce multiple videos from a list of topics
 * @param {string[]} topics - Array of topic strings
 * @param {Object} options - Same as runPipeline options
 * @returns {Promise<Array>} Array of results
 */
export async function runBatch(topics, options = {}) {
  log(`📦 Batch pipeline: ${topics.length} videos`);

  const results = [];
  for (let i = 0; i < topics.length; i++) {
    log(`Processing ${i + 1}/${topics.length}: "${topics[i]}"`);
    try {
      const result = await runPipeline(topics[i], options);
      results.push({ topic: topics[i], ...result });
    } catch (err) {
      error(`Failed on topic "${topics[i]}": ${err.message}`);
      results.push({ topic: topics[i], error: err.message });
    }
  }

  const successful = results.filter(r => !r.error).length;
  success(`Batch complete: ${successful}/${topics.length} videos generated`);

  // Save batch results
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  const batchPath = path.join(OUTPUT_DIR, `batch-${Date.now()}.json`);
  fs.writeFileSync(batchPath, JSON.stringify(results, null, 2));
  success(`Batch results saved: ${batchPath}`);

  return results;
}

// CLI entry point
const isMain = process.argv[1]?.endsWith('orchestrator.js');
if (isMain) {
  const args = process.argv.slice(2);
  const command = args[0];

  if (!command) {
    console.log(`
🎬 AI Avatar Video Pipeline v2 (HeyGen CLI)

Usage:
  node src/orchestrator.js "Your video topic"           Generate video from topic
  node src/orchestrator.js --batch topics.txt            Generate multiple videos
  node src/orchestrator.js --list-avatars                List available avatars
  node src/orchestrator.js --test                        Run connectivity test

Options:
  --no-script          Skip Claude script generation (use topic as prompt)
  --avatar-id ID       Use specific avatar
  --voice-id ID        Use specific voice
  --portrait            Portrait orientation (default: landscape)
  --no-download         Don't download video file

Examples:
  node src/orchestrator.js "3 ways AI saves businesses time"
  node src/orchestrator.js --avatar-id avt_angela_01 --voice-id abc123 "Welcome video"
  node src/orchestrator.js --no-script "Product demo in 30 seconds"
    `);
    process.exit(0);
  }

  // Parse options
  const opts = {};
  const positional = [];
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--no-script') opts.useScript = false;
    else if (args[i] === '--portrait') opts.orientation = 'portrait';
    else if (args[i] === '--no-download') opts.download = false;
    else if (args[i] === '--avatar-id' && args[i+1]) opts.avatarId = args[++i];
    else if (args[i] === '--voice-id' && args[i+1]) opts.voiceId = args[++i];
    else if (args[i] === '--list-avatars') { command = '--list-avatars'; }
    else if (args[i] === '--test') { command = '--test'; }
    else if (args[i] === '--batch' && args[i+1]) { opts.batchFile = args[++i]; command = '--batch'; }
    else if (!args[i].startsWith('--')) positional.push(args[i]);
  }

  const topic = positional.join(' ');

  (async () => {
    try {
      if (command === '--list-avatars') {
        const avatars = await listAvatars();
        console.log(`Found ${avatars.length} avatars:`);
        avatars.slice(0, 20).forEach(a => {
          console.log(`  ${a.avatar_id}: ${a.avatar_name || 'unnamed'}`);
        });
      } else if (command === '--test') {
        console.log('Testing HeyGen CLI connectivity...');
        const authed = await authenticate();
        if (authed) {
          success('HeyGen CLI authenticated ✅');
        } else {
          error('HeyGen CLI not authenticated. Set HEYGEN_API_KEY or run: heygen auth login');
          process.exit(1);
        }
      } else if (command === '--batch') {
        const topics = fs.readFileSync(opts.batchFile, 'utf8').split('\n').filter(t => t.trim());
        await runBatch(topics, opts);
      } else if (topic) {
        const result = await runPipeline(topic, opts);
        console.log('\n📊 Pipeline Result:');
        console.log(JSON.stringify(result, null, 2));
      } else {
        error('No topic provided. Usage: node src/orchestrator.js "Your video topic"');
        process.exit(1);
      }
    } catch (err) {
      error(`Pipeline failed: ${err.message}`);
      process.exit(1);
    }
  })();
}

export default { runPipeline, runPipelineWithAvatar, runBatch, listAvatars, authenticate };