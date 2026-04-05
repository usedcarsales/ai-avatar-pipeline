# AI Avatar Video Pipeline

Automated video production pipeline that turns a topic or script into a finished AI avatar video using Fish Audio (TTS) + HeyGen (avatar rendering).

## Stack

| Component | Service | Cost |
|-----------|---------|------|
| Voice / TTS | Fish Audio API | ~$0.006/video |
| Avatar Video | HeyGen Engine III | ~$2.00/video (2 min) |
| Script Generation | Claude (Anthropic) | ~$0.01/video |
| **Total** | | **~$2/video** |

30 videos/month ≈ **$70/mo all-in**. Sell at $50–$150/video = 95%+ gross margin.

## Project Structure

```
ai-avatar-pipeline/
├── src/
│   ├── orchestrator.js       # Main pipeline runner
│   ├── scriptGenerator.js    # LLM script generation (Claude)
│   ├── voiceSynth.js         # Fish Audio TTS integration
│   ├── avatarRenderer.js     # HeyGen avatar video integration
│   ├── test/
│   │   └── manualTest.js     # End-to-end manual test
│   └── utils/
│       └── logger.js         # Logging utility
├── research/                 # Phase 1 research docs
│   ├── target-audience-analysis.md
│   ├── competitor-analysis.md
│   ├── technical-requirements.md
│   └── content-strategy.md
├── output/                   # Generated audio/video (gitignored)
├── .env.example
├── package.json
└── README.md
```

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/usedcarsales/ai-avatar-pipeline
cd ai-avatar-pipeline

# 2. Install dependencies
npm install

# 3. Configure environment
cp .env.example .env
# Edit .env and fill in your API keys:
#   - FISH_AUDIO_API_KEY  (https://fish.audio/)
#   - HEYGEN_API_KEY      (https://app.heygen.com/avatar?nav=API)
#   - ANTHROPIC_API_KEY   (https://console.anthropic.com/)

# 4. Run a test
npm test
```

## Usage

```bash
# Generate a video from a topic
node src/orchestrator.js "3 ways AI avatars save businesses 10 hours per week"

# Or use npm script
npm run generate
```

### Programmatic

```javascript
import { runPipeline } from './src/orchestrator.js';

const result = await runPipeline('Your video topic here', {
  avatarId: 'your-avatar-id',   // from HeyGen avatar library
  voiceId: 'your-voice-id',     // from Fish Audio voice library
  style: 'professional',         // professional | casual | educational
  length: 'medium'               // short | medium | long
});

console.log(result.videoUrl);    // HeyGen video URL
console.log(result.cost);        // estimated $ cost
```

## API Keys

### Fish Audio
1. Sign up at https://fish.audio/
2. Go to Account → API Keys
3. Create a new key and add to `.env`

### HeyGen
1. Sign up at https://www.heygen.com/ (Creator plan $29/mo or pay-as-you-go)
2. Go to https://app.heygen.com/avatar?nav=API
3. Generate API key and add to `.env`
4. To list available avatar IDs: `node -e "import('./src/avatarRenderer.js').then(m => m.listAvatars())"`

### Fish Audio Voices
To list available voice IDs:
```bash
node -e "import('./src/voiceSynth.js').then(m => m.listVoices().then(console.log))"
```

## Research

See the [`research/`](./research/) folder for Phase 1 findings:
- Target audience analysis
- Competitor analysis (HeyGen vs Synthesia vs D-ID vs DeepReel)
- Technical requirements & API docs
- Content strategy framework

## Roadmap

- [x] Phase 1: Research & architecture
- [ ] Phase 2: Core pipeline modules (this build)
- [ ] Phase 3: Content engine & batch production
- [ ] Phase 4: Analytics & multi-brand expansion
