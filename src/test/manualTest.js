// manualTest.js — End-to-end manual test for the AI Avatar Pipeline
// Run: npm test  OR  node src/test/manualTest.js

import 'dotenv/config';
import fs from 'fs';
import path from 'path';
import { generateScript } from '../scriptGenerator.js';
import { synthesize, listVoices } from '../voiceSynth.js';
import { render, listAvatars, estimateCost } from '../avatarRenderer.js';
import { log, success, error, warn } from '../utils/logger.js';

const OUTPUT_DIR = process.env.OUTPUT_DIR || './output';
const TEST_TOPIC = '3 ways AI avatars save businesses 10 hours per week';

async function runManualTest() {
  console.log('\n🧪 ==========================================');
  console.log('   AI Avatar Pipeline — Manual Test');
  console.log('==========================================\n');

  const results = {
    topic: TEST_TOPIC,
    timestamp: new Date().toISOString(),
    steps: {},
    success: false
  };

  const startTime = Date.now();

  // ── Step 1: Check API keys ─────────────────────────────────────────────────
  log('Step 1: Checking API keys...');
  const keys = {
    ANTHROPIC_API_KEY: !!process.env.ANTHROPIC_API_KEY,
    FISH_AUDIO_API_KEY: !!process.env.FISH_AUDIO_API_KEY,
    HEYGEN_API_KEY: !!process.env.HEYGEN_API_KEY
  };

  Object.entries(keys).forEach(([key, present]) => {
    if (present) success(`  ${key}: ✅`);
    else warn(`  ${key}: ❌ NOT SET`);
  });

  results.steps.apiKeys = keys;
  const allKeysPresent = Object.values(keys).every(Boolean);

  if (!allKeysPresent) {
    warn('\nSome API keys are missing. Skipping live API calls.');
    warn('Copy .env.example to .env and fill in your keys to run full test.\n');
  }

  // ── Step 2: Generate script ────────────────────────────────────────────────
  log('\nStep 2: Generating script...');
  const scriptStart = Date.now();

  let scriptResult;
  if (keys.ANTHROPIC_API_KEY) {
    try {
      scriptResult = await generateScript(TEST_TOPIC, {
        length: 'short',
        style: 'professional',
        targetAudience: 'business owners and marketers'
      });
      results.steps.script = {
        success: true,
        title: scriptResult.title,
        wordCount: scriptResult.script.split(/\s+/).length,
        estimatedDuration: scriptResult.estimatedDuration,
        timeMs: Date.now() - scriptStart
      };
      success(`Script generated in ${Date.now() - scriptStart}ms`);
      console.log(`\n  Title: "${scriptResult.title}"`);
      console.log(`  Preview: "${scriptResult.script.substring(0, 120)}..."\n`);
    } catch (err) {
      error(`Script generation failed: ${err.message}`);
      results.steps.script = { success: false, error: err.message };
      scriptResult = {
        title: 'Test Video',
        script: TEST_TOPIC + '. This is a test script for the AI Avatar Pipeline.',
        estimatedDuration: 30
      };
    }
  } else {
    warn('Skipping script generation (no API key) — using placeholder');
    scriptResult = {
      title: 'Test Video (placeholder)',
      script: 'This is a placeholder script. Add your Anthropic API key to test script generation.',
      estimatedDuration: 10
    };
    results.steps.script = { success: false, reason: 'No API key' };
  }

  // ── Step 3: List available voices ──────────────────────────────────────────
  log('Step 3: Listing Fish Audio voices...');
  if (keys.FISH_AUDIO_API_KEY) {
    try {
      const voices = await listVoices();
      results.steps.fishAudio = {
        success: true,
        voiceCount: voices.length,
        sampleVoices: voices.slice(0, 3).map(v => ({ id: v._id, name: v.title }))
      };
      success(`Found ${voices.length} voices`);
      if (voices.length > 0) {
        console.log('  Sample voices:');
        voices.slice(0, 3).forEach(v => console.log(`    - ${v.title} (${v._id})`));
      }
    } catch (err) {
      error(`Fish Audio listing failed: ${err.message}`);
      results.steps.fishAudio = { success: false, error: err.message };
    }
  } else {
    warn('Skipping Fish Audio test (no API key)');
    results.steps.fishAudio = { success: false, reason: 'No API key' };
  }

  // ── Step 4: List available avatars ─────────────────────────────────────────
  log('Step 4: Listing HeyGen avatars...');
  if (keys.HEYGEN_API_KEY) {
    try {
      const avatars = await listAvatars();
      results.steps.heyGen = {
        success: true,
        avatarCount: avatars.length,
        sampleAvatars: avatars.slice(0, 3).map(a => ({ id: a.avatar_id, name: a.avatar_name }))
      };
      success(`Found ${avatars.length} avatars`);
      if (avatars.length > 0) {
        console.log('  Sample avatars:');
        avatars.slice(0, 3).forEach(a => console.log(`    - ${a.avatar_name} (${a.avatar_id})`));
      }
    } catch (err) {
      error(`HeyGen avatar listing failed: ${err.message}`);
      results.steps.heyGen = { success: false, error: err.message };
    }
  } else {
    warn('Skipping HeyGen test (no API key)');
    results.steps.heyGen = { success: false, reason: 'No API key' };
  }

  // ── Step 5: Cost estimation ─────────────────────────────────────────────────
  log('\nStep 5: Cost estimation for test video...');
  const estimatedDuration = scriptResult.estimatedDuration || 60;
  const costIII = estimateCost(estimatedDuration, 'III');
  const costIV = estimateCost(estimatedDuration, 'IV');
  success(`Estimated duration: ${estimatedDuration}s`);
  success(`Engine III cost: $${costIII.toFixed(4)}`);
  success(`Engine IV cost: $${costIV.toFixed(4)}`);
  results.steps.costEstimate = { duration: estimatedDuration, costEngineIII: costIII, costEngineIV: costIV };

  // ── Summary ─────────────────────────────────────────────────────────────────
  const totalTime = ((Date.now() - startTime) / 1000).toFixed(1);
  results.success = true;
  results.totalTimeSeconds = parseFloat(totalTime);

  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  const resultsPath = path.join(OUTPUT_DIR, 'test-results.json');
  fs.writeFileSync(resultsPath, JSON.stringify(results, null, 2));

  console.log('\n==========================================');
  console.log('   Test Summary');
  console.log('==========================================');
  console.log(`  Script: ${results.steps.script?.success ? '✅' : '⚠️ '}`);
  console.log(`  Fish Audio: ${results.steps.fishAudio?.success ? '✅' : '⚠️ '}`);
  console.log(`  HeyGen: ${results.steps.heyGen?.success ? '✅' : '⚠️ '}`);
  console.log(`  Cost/video (Engine III, ${estimatedDuration}s): $${costIII.toFixed(4)}`);
  console.log(`  Total time: ${totalTime}s`);
  console.log(`  Results saved: ${resultsPath}`);
  console.log('\n  To run full end-to-end test:');
  console.log('  1. Set all API keys in .env');
  console.log('  2. Set DEFAULT_AVATAR_ID and DEFAULT_VOICE_ID in .env');
  console.log('  3. Run: node src/orchestrator.js "Your topic here"');
  console.log('==========================================\n');
}

runManualTest().catch(err => {
  error(`Test failed: ${err.message}`);
  console.error(err);
  process.exit(1);
});
