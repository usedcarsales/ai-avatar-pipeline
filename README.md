# AI Avatar Video Pipeline v2

Automated video production pipeline using **HeyGen CLI** + **Claude** — from topic to finished video in one command.

## What Changed in v2

The original pipeline used custom REST API calls to Fish Audio and HeyGen. HeyGen's official CLI ([docs](https://developers.heygen.com/cli)) now handles video generation, voice synthesis, avatar listing, and downloading — so we replaced ~300 lines of custom HTTP code with CLI calls.

**Old:** `avatarRenderer.js` + `voiceSynth.js` (REST API polling, manual auth, custom download)
**New:** `videoRenderer.js` (HeyGen CLI with `--wait` flag, built-in auth, built-in download)

Fish Audio is still supported for custom voice cloning, but no longer required for basic pipeline operation.

## Stack

| Component | Service | Cost |
|-----------|---------|------|
| Script Generation | Claude (Anthropic) | ~$0.01/video |
| Avatar Video | HeyGen CLI (Video Agent) | ~$0.033/sec |
| Avatar Video (specific avatar) | HeyGen CLI (Avatar IV) | ~$0.10/sec |
| Voice (included in HeyGen) | HeyGen built-in | Included |
| Custom Voice Cloning | Fish Audio (optional) | ~$0.006/video |
| B-roll / Scene Video | OpenClaw native (optional) | Per-clip |

## Prerequisites

1. **Node.js 18+**
2. **HeyGen CLI** — install with:
   ```bash
   curl -fsSL https://static.heygen.ai/cli/install.sh | bash
   ```
3. **HeyGen API key** — get from https://app.heygen.com/settings/api
4. **Anthropic API key** (for script generation)

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/usedcarsales/ai-avatar-pipeline
cd ai-avatar-pipeline

# 2. Install dependencies
npm install

# 3. Install HeyGen CLI
curl -fsSL https://static.heygen.ai/cli/install.sh | bash

# 4. Authenticate HeyGen
heygen auth login
# Or set environment variable:
export HEYGEN_API_KEY=your_key_here

# 5. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 6. Run a test
npm test
```

## Usage

### Generate a video from a topic (simplest mode)
```bash
# HeyGen handles everything: script, avatar, voice, layout
node src/orchestrator.js "3 ways AI avatars save businesses 10 hours per week"
```

### Generate with specific avatar and voice
```bash
node src/orchestrator.js --avatar-id avt_angela_01 --voice-id abc123 "Welcome to our company"
```

### Skip Claude script generation (use topic as-is)
```bash
node src/orchestrator.js --no-script "Product demo in 30 seconds"
```

### List available avatars
```bash
node src/orchestrator.js --list-avatars
```

### Batch produce videos from a file
```bash
node src/orchestrator.js --batch topics.txt
```

### Programmatic
```javascript
import { runPipeline, runPipelineWithAvatar, runBatch } from './src/orchestrator.js';

// Simple mode — Video Agent handles everything
const result = await runPipeline('Your video topic here', {
  orientation: 'landscape',
  download: true
});
console.log(result.videoUrl);

// Full control — specific avatar and voice
const result = await runPipelineWithAvatar(script, 'avatar-id', 'voice-id');

// Batch mode
const results = await runBatch(['topic 1', 'topic 2', 'topic 3']);
```

## Project Structure

```
ai-avatar-pipeline/
├── src/
│   ├── orchestrator.js       # Main pipeline runner (v2 — HeyGen CLI)
│   ├── scriptGenerator.js    # Claude-powered script generation
│   ├── videoRenderer.js      # HeyGen CLI wrapper (replaces avatarRenderer + voiceSynth)
│   ├── test/
│   │   └── manualTest.js     # End-to-end test
│   └── utils/
│       └── logger.js         # Logging utility
├── research/                 # Phase 1 research docs
│   ├── target-audience-analysis.md
│   ├── competitor-analysis.md
│   ├── technical-requirements.md
│   └── content-strategy.md
├── output/                   # Generated videos (gitignored)
├── .env.example
├── package.json
└── README.md
```

## Key Differences from v1

| Feature | v1 (REST API) | v2 (HeyGen CLI) |
|---------|---------------|------------------|
| Auth | Manual API key headers | `heygen auth login` or env var |
| Video generation | Custom POST + poll loop | `heygen video-agent create --wait` |
| Avatar listing | Custom GET request | `heygen avatar list` |
| Download | Custom fetch + write | `heygen video download` |
| Voice synthesis | Fish Audio (separate) | HeyGen built-in (or Fish Audio optional) |
| Polling | 50+ lines of custom code | `--wait` flag |
| API version | v1 (deprecated) | v3 (current) |
| Avatar engine | III (deprecated July 2026) | IV/V (future-proof) |

## ⚠️ Important Notes

- **Avatar III is deprecated** — HeyGen v3 API (used by CLI) targets Avatar IV/V. Migrate any existing workflows.
- **HeyGen CLI requires WSL on Windows** — native Windows support coming soon. Both our rigs run WSL2 ✅
- **Video Agent mode** is the simplest way to generate videos. It handles scripting, avatar selection, and layout automatically. Use specific avatar/voice when you need brand consistency.

## Roadmap

- [x] Phase 1: Research & architecture
- [x] Phase 2: Pipeline build (v2 — HeyGen CLI)
- [ ] Phase 3: Content engine & batch production
- [ ] Phase 4: Analytics & multi-brand expansion