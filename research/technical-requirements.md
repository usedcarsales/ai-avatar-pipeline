# Technical Requirements — AI Avatar Video Pipeline

## Overview
This document defines the exact API integrations, technical architecture, rate limits, quality tiers, and integration requirements for the AI Avatar Video Pipeline.

---

## Core API Stack

### 1. Fish Audio — TTS / Voice Synthesis
- **Base URL:** https://api.fish.audio
- **Auth:** API key in header `Authorization: Bearer {API_KEY}`
- **Docs:** https://docs.fish.audio
- **Key endpoints:**
  - `POST /v1/tts` — Text-to-speech generation
  - `POST /v1/model` — Upload/train voice clone model
  - `GET /v1/model` — List available voice models
- **Streaming:** Real-time streaming supported (WebSocket or chunked HTTP)
- **Voice cloning:** Minimum 10 seconds of audio required to create a clone
- **Supported languages:** English, Japanese, Korean, Chinese, French, German, Arabic, Spanish (8+ core, expanding)
- **Output formats:** MP3, WAV, PCM
- **Rate limits:** Per plan (verify on account dashboard post-signup)
- **Pricing tier to use:** Pro (~$9.99/mo per project brief)
- **Integration module:** `voiceSynth.js`

```javascript
// Fish Audio TTS integration pattern
const fishAudioTTS = async (text, voiceId) => {
  const response = await fetch('https://api.fish.audio/v1/tts', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.FISH_AUDIO_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      text,
      reference_id: voiceId,
      format: 'mp3',
      mp3_bitrate: 128
    })
  });
  return response; // stream or buffer
};
```

---

### 2. DeepReel — Avatar Video Generation (Primary Budget Tier)
- **App URL:** https://app.deepreel.com
- **API docs:** Not prominently documented — primarily web platform
- **Auth:** Session-based (web app) — API access may require Business/Enterprise plan
- **Integration approach for Phase 1:** 
  - Use web interface for initial video generation and quality testing
  - Investigate API availability at Business tier
  - Fallback: browser automation if no API available
- **Credit model:**
  - Avatar video: 1 credit/sec
  - Pro plan: 600 credits/mo = **10 minutes of avatar video/mo** at $25/mo
  - Business plan: 1,500 credits/team/mo = **25 minutes of avatar video/mo** at $30/seat/mo
- **Video quality:** 720p (Starter/Pro), 1080p (Business+)
- **Max video length:** 5 min (Pro), 8 min (Business)
- **Input types:** Prompt, URL, PDF, text script
- **Integration module:** `avatarRenderer.js`

**⚠️ Action Required:** Verify if DeepReel has a public REST API before Phase 2 coding. If not, evaluate:
- Using HeyGen API exclusively
- Scripting DeepReel via Playwright automation

---

### 3. HeyGen — Avatar Video Generation (Premium Tier)
- **Base URL:** `https://api.heygen.com`
- **Auth:** `X-API-KEY: {API_KEY}` header
- **Docs:** https://docs.heygen.com
- **Integration approach:** REST API — fully documented, production-ready
- **Key endpoints:**
  - `POST /v1/video_agent/generate` — Prompt to video
  - `POST /v1/video/generate` — Script + avatar to video
  - `GET /v1/video_status.get?video_id={id}` — Poll rendering status
  - `GET /v1/avatars` — List available avatars
  - `POST /v1/video_translate/translate` — Video translation
- **API pricing (pay-as-you-go):**
  - Public Avatar Engine III: **$0.0167/sec** = ~$1.00/min = **$60/hr of video**
  - Public Avatar Engine IV: **$0.1/sec** = ~$6.00/min = very expensive at scale
  - Digital Twin Engine III: **$0.0333/sec** = ~$2.00/min
  - Prompt-to-Video: **$0.0333/sec**
- **Recommended engine:** Engine III for all production work (6x cheaper than IV)
- **Rate limits:** Check https://docs.heygen.com/reference/limits
- **Video generation is async:** Submit job → poll for completion → download
- **Integration module:** `avatarRenderer.js`

```javascript
// HeyGen video generation pattern
const generateHeyGenVideo = async (scriptText, avatarId) => {
  // 1. Submit job
  const job = await fetch('https://api.heygen.com/v1/video/generate', {
    method: 'POST',
    headers: {
      'X-API-KEY': process.env.HEYGEN_API_KEY,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      video_inputs: [{
        character: { type: 'avatar', avatar_id: avatarId },
        voice: { type: 'text', input_text: scriptText }
      }],
      dimension: { width: 1280, height: 720 }
    })
  });
  const { data: { video_id } } = await job.json();

  // 2. Poll for completion
  let status = 'pending';
  while (status !== 'completed') {
    await sleep(5000);
    const poll = await fetch(`https://api.heygen.com/v1/video_status.get?video_id=${video_id}`, {
      headers: { 'X-API-KEY': process.env.HEYGEN_API_KEY }
    });
    const result = await poll.json();
    status = result.data.status;
    if (status === 'failed') throw new Error('HeyGen render failed');
  }
  return result.data.video_url;
};
```

---

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI Avatar Video Pipeline                       │
│                                                                   │
│  INPUT                                                            │
│  ─────                                                            │
│  Topic / URL / Script / PDF                                       │
│         │                                                         │
│         ▼                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐        │
│  │ scriptGen.js │───▶│ voiceSynth.js│───▶│avatarRender  │        │
│  │ (GPT/Claude) │    │ (Fish Audio) │    │.js (DeepReel │        │
│  └──────────────┘    └──────────────┘    │ or HeyGen)   │        │
│                                          └──────┬───────┘        │
│                                                 │                 │
│                                                 ▼                 │
│                                      ┌──────────────────┐        │
│                                      │ postProduction.js│        │
│                                      │ (captions, music,│        │
│                                      │  branding)       │        │
│                                      └──────┬───────────┘        │
│                                             │                     │
│                                             ▼                     │
│                                      ┌──────────────┐            │
│                                      │  distribute  │            │
│                                      │  .js         │            │
│                                      │ (YouTube,    │            │
│                                      │  social,LMS) │            │
│                                      └──────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Module Breakdown (Phase 2 Build)

| Module | File | API Used | Priority |
|--------|------|----------|----------|
| Script Generator | `scriptGenerator.js` | OpenAI / Claude API | P0 |
| Voice Synthesizer | `voiceSynth.js` | Fish Audio API | P0 |
| Avatar Renderer | `avatarRenderer.js` | DeepReel / HeyGen API | P0 |
| Orchestrator | `orchestrator.js` | Internal | P0 |
| Post-Production | `postProduction.js` | FFmpeg (local) | P1 |
| Distribution | `distribute.js` | YouTube Data API v3 | P1 |
| Analytics | `analytics.js` | YouTube Analytics API | P2 |

---

## Environment Variables Required

```bash
# Fish Audio
FISH_AUDIO_API_KEY=

# HeyGen
HEYGEN_API_KEY=

# DeepReel
DEEPREEL_API_KEY=           # TBD - verify availability

# LLM for script generation
ANTHROPIC_API_KEY=           # Claude for script gen
OPENAI_API_KEY=              # GPT-4 fallback

# YouTube Distribution
YOUTUBE_CLIENT_ID=
YOUTUBE_CLIENT_SECRET=
YOUTUBE_REFRESH_TOKEN=

# Pipeline Config
DEFAULT_VIDEO_ENGINE=deepreel   # 'deepreel' | 'heygen'
DEFAULT_AVATAR_ID=
DEFAULT_VOICE_ID=
OUTPUT_DIR=./output
```

---

## Quality Tiers

| Tier | Engine | Est. Cost/Video (2min) | Use Case |
|------|--------|----------------------|----------|
| Budget | DeepReel Pro | ~$0.08 (0.8 credits) | Testing, high-volume social |
| Standard | HeyGen Engine III | ~$2.00 | Course content, B2B explainers |
| Premium | HeyGen Engine IV | ~$12.00 | Client deliverables, ads |
| Custom | HeyGen Digital Twin III | ~$4.00 | Personal brand, consulting |

---

## Technical Constraints & Gotchas

1. **HeyGen video generation is async** — must poll, not a synchronous response. Build queue + retry logic.
2. **DeepReel API availability** — not confirmed. If web-only, use HeyGen exclusively or add Playwright automation.
3. **Fish Audio voice cloning** — 10 second minimum audio, but more = better quality. Recommend 30–60 seconds.
4. **Video file handling** — rendered videos can be 50–500MB. Need reliable temp storage + cleanup.
5. **Rate limiting** — Fish Audio and HeyGen will rate limit on burst. Queue all API calls.
6. **Concurrent rendering** — HeyGen accepts concurrent jobs but billing is per-second of completed video.
7. **Engine selection** — Engine IV is 6x the cost of Engine III. Default to III, gate IV behind premium flag.

---

## Phase 2 Development Requirements
- Node.js 18+ (ESM modules)
- FFmpeg installed locally for post-production
- GitHub repo: https://github.com/usedcarsales/ai-avatar-pipeline
- All API keys in `.env` (never commit)
- Test suite covering: TTS generation, video rendering, orchestration flow

---

## Sources
- HeyGen API docs: https://docs.heygen.com
- HeyGen API limits/pricing: https://docs.heygen.com/reference/limits
- Fish Audio docs: https://docs.fish.audio
- DeepReel platform: https://deepreel.com
- D-ID API docs: https://docs.d-id.com/reference/get-started
