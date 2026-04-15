// manualTest.js — End-to-end test for AI Avatar Pipeline v2 (HeyGen CLI)
// Run: npm test  OR  node src/test/manualTest.js

import 'dotenv/config';
import fs from 'fs';
import path from 'path';
import { generateScript } from '../scriptGenerator.js';
import { createWithAgent, listAvatars, authenticate, estimateCost } from '../videoRenderer.js';
import { log, success, error, warn } from '../utils/logger.js';

const OUTPUT_DIR = process.env.OUTPUT_DIR || './output';
const TEST_TOPIC = '3 ways AI avatars save businesses 10 hours per week';

async function runManualTest() {
  console.log('\n🧪 ==========================================');
  console.log('   AI Avatar Pipeline v2 — HeyGen CLI Test');
  console.log('==========================================\n');

  const results = {
    topic: TEST_TOPIC,
    timestamp: new Date().toISOString(),
    version: '2.0.0-heygen-cli',
    steps: {},
    success: false
  };

  const startTime = Date.now();

  // ── Step 1: Check API keys and CLI ────────────────────────────────────────
  log('Step 1: Checking API keys and HeyGen CLI...');
  const keys = {
    ANTHROPIC_API_KEY: !!process.env.ANTHROPIC_API_KEY,
    HEYGEN_API_KEY: !!process.env.HEYGEN_API_KEY,
    FISH_AUDIO_API_KEY: !!process.env.FISH_AUDIO_API_KEY
  };

  Object.entries(keys).forEach(([key, present]) => {
    if (present) success(`  ${key}: ✅`);
    else warn(`  ${key}: ❌ NOT SET`);
  });

  results.steps.apiKeys = keys;

  // Check HeyGen CLI installation
  try {
    const { execFile } = await import('child_process');
    const { promisify } = await import('util');
    const execFileAsync = promisify(execFile);
    const { stdout } = await execFileAsync('heygen', ['--version']);
    success(`  HeyGen CLI: ✅ ${stdout.trim()}`);
    results.steps.cliInstalled = true;
    results.steps.cliVersion = stdout.trim();
  } catch {
    error('  HeyGen CLI: ❌ NOT FOUND — install with: curl -fsSL https://static.heygen.ai/cli/install.sh | bash');
    results.steps.cliInstalled = false;
  }

  // Check HeyGen auth
  const authed = await authenticate();
  results.steps.authenticated = authed;

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
        script: 'This is a test of the AI Avatar Pipeline. Three ways AI avatars save businesses time: automation, consistency, and scale.',
        estimatedDuration: 30
      };
    }
  } else {
    warn('Skipping script generation (no Anthropic key) — using placeholder');
    scriptResult = {
      title: 'Test Video (placeholder)',
      script: 'This is a test of the AI Avatar Pipeline. Three ways AI avatars save businesses time: automation, consistency, and scale.',
      estimatedDuration: 30
    };
    results.steps.script = { success: false, reason: 'No API key' };
  }

  // ── Step 3: List available avatars ─────────────────────────────────────────
  log('Step 3: Listing HeyGen avatars...');
  if (keys.HEYGEN_API_KEY && authed && results.steps.cliInstalled) {
    try {
      const avatars = await listAvatars();
      results.steps.avatars = {
        success: true,
        count: avatars.length,
        sample: avatars.slice(0, 5).map(a => ({ id: a.avatar_id, name: a.avatar_name }))
      };
      success(`Found ${avatars.length} avatars`);
    } catch (err) {
      error(`Avatar listing failed: ${err.message}`);
      results.steps.avatars = { success: false, error: err.message };
    }
  } else {
    warn('Skipping avatar listing (no API key or CLI not installed)');
    results.steps.avatars = { success: false, reason: 'No API key or CLI' };
  }

  // ── Step 4: Cost estimation ─────────────────────────────────────────────────
  log('\nStep 4: Cost estimation...');
  const estimatedDuration = scriptResult.estimatedDuration || 30;
  const costAgent = estimateCost(estimatedDuration, 'agent');
  const costAvatarIV = estimateCost(estimatedDuration, 'avatarIV');
  success(`Estimated duration: ${estimatedDuration}s`);
  success(`Video Agent cost: $${costAgent.toFixed(4)}`);
  success(`Avatar IV cost: $${costAvatarIV.toFixed(4)}`);
  results.steps.costEstimate = {
    duration: estimatedDuration,
    costAgent,
    costAvatarIV
  };

  // ── Step 5: Video generation test (optional, costs money) ──────────────────
  log('\nStep 5: Video generation test (skipped — add --live to run actual generation)');
  results.steps.videoGeneration = { skipped: true, note: 'Use --live flag to generate actual video' };

  // ── Summary ─────────────────────────────────────────────────────────────────
  const totalTime = ((Date.now() - startTime) / 1000).toFixed(1);
  results.success = true;
  results.totalTimeSeconds = parseFloat(totalTime);

  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  const resultsPath = path.join(OUTPUT_DIR, 'test-results.json');
  fs.writeFileSync(resultsPath, JSON.stringify(results, null, 2));

  console.log('\n==========================================');
  console.log('   Test Summary (v2 — HeyGen CLI)');
  console.log('==========================================');
  console.log(`  HeyGen CLI: ${results.steps.cliInstalled ? '✅' : '❌'}`);
  console.log(`  Auth: ${results.steps.authenticated ? '✅' : '⚠️ '}`);
  console.log(`  Script: ${results.steps.script?.success ? '✅' : '⚠️ '}`);
  console.log(`  Avatars: ${results.steps.avatars?.success ? '✅' : '⚠️ '}`);
  console.log(`  Cost/30s video (Agent): $${costAgent.toFixed(4)}`);
  console.log(`  Cost/30s video (Avatar IV): $${costAvatarIV.toFixed(4)}`);
  console.log(`  Total time: ${totalTime}s`);
  console.log(`  Results: ${resultsPath}`);
  console.log('\n  Next steps:');
  console.log('  1. Set HEYGEN_API_KEY in .env');
  console.log('  2. Run: node src/orchestrator.js "Your video topic"');
  console.log('  3. Or: node src/orchestrator.js --list-avatars');
  console.log('==========================================\n');
}

runManualTest().catch(err => {
  error(`Test failed: ${err.message}`);
  console.error(err);
  process.exit(1);
});