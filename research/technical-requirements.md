# Technical Requirements — AI Avatar Pipeline APIs
## Particulate LLC / AI Avatar Video Pipeline Project

**Date:** April 5, 2026  
**Researcher:** Servius  
**Focus:** Fish Audio (TTS/Voice), DeepReel (Avatar), HeyGen (Avatar), D-ID (Avatar)

---

## Architecture Overview

The AI Avatar Video Pipeline consists of three core layers:

```
┌─────────────────────────────────────────┐
│  CONTENT LAYER                          │
│  Script → Prompt → Text                 │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  VOICE LAYER (Fish Audio API)           │
│  Text → Natural speech audio (.mp3)     │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  AVATAR LAYER (HeyGen / D-ID / DeepReel)│
│  Audio + Avatar config → Video (.mp4)   │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  DISTRIBUTION LAYER                     │
│  Video → Platform upload (YouTube, etc.)│
└─────────────────────────────────────────┘
```

Alternatively, use a unified platform (HeyGen handles voice + avatar in one call).

---

## 1. Fish Audio API

**Website:** fish.audio  
**Use case:** High-quality TTS and voice cloning for audio generation  
**SDK:** Python, JavaScript (official)

### Pricing (live, April 2026)
| Model | Price | Notes |
|-------|-------|-------|
| S2 Pro (TTS) | $15.00 / million UTF-8 bytes | Highest quality, latest model |
| S1 (TTS) | $15.00 / million UTF-8 bytes | Standard quality |
| transcribe-1 (ASR) | $0.36 / hour | Audio → text |
| Voice cloning | Included in TTS pricing | Needs ~10 seconds of reference audio |

**Cost calculation for typical use:**
- 1,000-word script ≈ ~6,000 UTF-8 bytes
- 1 video = ~$0.09 in Fish Audio costs
- 10 videos/month = ~$0.90/month
- 100 videos/month = ~$9/month
- 1,000 videos/month = ~$90/month (still under $15/million threshold)

**Free tier:** Free monthly generations (amount not disclosed on public page; confirm on signup)

### API Integration
```bash
# TTS endpoint
POST https://api.fish.audio/v1/tts
Authorization: Bearer $FISH_API_KEY
Content-Type: application/json

{
  "text": "Your script content here",
  "reference_id": "voice-model-id"  # for voice cloning
}
# Returns: audio stream (.mp3)
```

```python
# Python SDK
from fishaudio import FishAudio
from fishaudio.utils import save

client = FishAudio(api_key="your_api_key_here")
audio = client.tts.convert(
    text="(excited) Welcome to our product demo!",
    reference_id="your-cloned-voice-id"
)
save(audio, "output.mp3")
```

```javascript
// JavaScript SDK
import { FishAudioClient, play } from "fish-audio";

const fishAudio = new FishAudioClient({ apiKey: "your_api_key_here" });
const audio = await fishAudio.textToSpeech.convert({
  text: "Hello! Welcome to Fish Audio."
});
// Stream or save to file
```

### Key Features
- 2,000,000+ community voice models available
- Voice cloning from as little as 10 seconds of reference audio
- Multi-language: English, Japanese, Korean, Chinese, French, German, Arabic, Spanish
- Emotion control in text (e.g., `(surprised)`, `(excited)`)
- Real-time streaming capable
- Commercial use requires paid plan
- REST API + Python SDK + JavaScript SDK

### Rate Limits
- Not publicly disclosed; contact Fish Audio for enterprise rate limits
- Pay-as-you-go: no hard limit at standard tiers

### Integration Requirements
- Fish Audio API key (from fish.audio)
- Python: `pip install fish-audio-sdk`
- JavaScript: `npm install fish-audio`

---

## 2. HeyGen API

**Website:** heygen.com  
**API docs:** docs.heygen.com

### Pricing
- API access included with Creator plan ($29/mo)
- API usage counted against plan minutes
- Creator plan: Unlimited video minutes (no hard cap stated)
- Enterprise: Dedicated API quotas

### Key API Capabilities
- Generate avatar videos from script + avatar ID
- List available avatars
- Create talking photo from image + audio
- Video translation (separate endpoint)
- Webhook notifications on completion

### Authentication
```bash
X-Api-Key: YOUR_HEYGEN_API_KEY
Content-Type: application/json
```

### Core Endpoint: Video Generation
```bash
POST https://api.heygen.com/v2/video/generate
{
  "video_inputs": [{
    "character": {
      "type": "avatar",
      "avatar_id": "YOUR_AVATAR_ID",
      "avatar_style": "normal"
    },
    "voice": {
      "type": "text",
      "input_text": "Your script here",
      "voice_id": "YOUR_VOICE_ID"
    },
    "background": {
      "type": "color",
      "value": "#FAFAFA"
    }
  }],
  "dimension": {
    "width": 1280,
    "height": 720
  }
}
```

### Response Pattern (Async)
1. Submit → get `video_id`
2. Poll status endpoint: `GET /v1/video.list?video_id=xxx`
3. When status = "completed" → download from `video_url`
4. Typical generation time: 1-5 minutes for a 1-minute video

### Webhook Support
```json
{
  "url": "https://your-server.com/heygen-webhook",
  "events": ["video.completed", "video.failed"]
}
```

### Rate Limits
- Concurrent video generation: depends on plan tier
- Free: 3 videos/month total
- Creator: No documented hard limit per minute; throttling may apply
- Recommend: Queue-based submission with exponential backoff

---

## 3. D-ID API

**Website:** d-id.com  
**API Docs:** docs.d-id.com  
**Best for:** Developer integration, photo-to-video, budget automation

### Pricing
- API usage deducted from plan balance (same pool as web usage)
- Pro plan: $29.99/mo, includes API access
- Minutes used via API = same cost as web

### Core Endpoint: Create Talk (Photo → Video)
```bash
POST https://api.d-id.com/talks
Authorization: Basic {base64(username:password)}
Content-Type: application/json

{
  "source_url": "https://your-image.com/photo.jpg",
  "script": {
    "type": "text",
    "input": "Your script here",
    "provider": {
      "type": "elevenlabs",
      "voice_id": "your-elevenlabs-voice-id"
    }
  },
  "config": {
    "fluent": true,
    "pad_audio": 0.0
  }
}
```

### Voice Provider Options (D-ID supports)
- Microsoft Azure TTS
- ElevenLabs (highest quality)
- Amazon Polly
- Google Cloud TTS
- D-ID built-in voices

### Response Pattern (Async)
1. Submit → get `id` field
2. Poll: `GET /talks/{id}` 
3. When `status = "done"` → `result_url` field = downloadable video
4. Typical time: 1-3 minutes

### Key Advantage
- **Well-documented API** — best developer docs of all platforms
- Photo-to-video requires just an image URL — no avatar setup needed
- ElevenLabs integration gives highest-quality voice without separate Fish Audio

### Rate Limits
- Not published; contact for enterprise
- Minutes deducted in 15-second intervals (rounded up)

---

## 4. DeepReel

**Website:** deepreel.com  
**API:** Not prominently documented; primarily UI-driven
**Use:** More suitable for manual workflow than automated API pipeline

### Credit System
| Feature | Credits |
|---------|---------|
| Avatar video | 1 credit/second |
| Audio generation | 0.1 credit/second |
| AI image generation | 2 credits/image |
| Custom avatar creation | 600 credits (one-time) |

**Pro plan ($25/mo):** 600 credits = 10 minutes avatar video/month

### Integration Options
- Canva integration (native plugin)
- Adobe integration
- API: Contact team@deepreel.com for API access details

### Assessment for Pipeline
⚠️ DeepReel is primarily a UI-based platform. For automated pipeline use, HeyGen or D-ID are more suitable. DeepReel is best for human-in-the-loop workflows via Canva/Adobe integration.

---

## 5. Fish Audio vs ElevenLabs Comparison

Both are voice generation APIs. Understanding the tradeoff:

| Feature | Fish Audio | ElevenLabs |
|---------|------------|------------|
| Pricing | $15/million bytes | $5/month (Starter), $22/month (Creator) |
| Voice models | 2M+ community | 1M+ community |
| Cloning speed | 10 seconds reference | 1 minute reference |
| Quality | Excellent | Excellent |
| API | REST + Python + JS SDK | REST + Python + JS SDK |
| Commercial rights | Paid plans | Paid plans |
| Emotion control | Yes (in text tags) | Yes (via settings) |
| **Best for pipeline** | High-volume pay-as-you-go | Low-volume subscription |

**Recommendation:** Fish Audio for scale (pay-per-use, lower at volume); ElevenLabs if already subscribed or needing specific voices.

---

## 6. Full Pipeline Architecture Options

### Option A: HeyGen-Only (Simplest)
```
Script → HeyGen API (voice + avatar + video) → Output .mp4
```
- Cost: $29/mo (Creator plan)
- Complexity: Low
- Quality: High
- Limit: Depends on plan

### Option B: Fish Audio + HeyGen (Best Quality)
```
Script → Fish Audio API → Custom voice .mp3
                    ↓
HeyGen API (avatar + video with custom audio) → Output .mp4
```
- Cost: $29/mo (HeyGen) + ~$3/mo (Fish Audio at normal volume) = ~$32/mo
- Complexity: Medium
- Quality: Highest (custom cloned voice + premium avatar)
- Limit: Effectively unlimited

### Option C: Fish Audio + D-ID (Budget API)
```
Script → Fish Audio API → Custom voice .mp3
                    ↓
D-ID API (photo + audio → video) → Output .mp4
```
- Cost: $29.99/mo (D-ID Pro) + ~$3/mo (Fish Audio) = ~$33/mo
- Complexity: Medium
- Quality: Good (lower avatar quality than HeyGen)
- Limit: D-ID plan minutes

### Option D: Fully Automated OpenClaw Pipeline
```
Scheduled cron/trigger
    → Servius generates script (AI)
    → Fish Audio API → voice .mp3
    → HeyGen API → avatar .mp4
    → YouTube/TikTok API → upload
    → Operator receives link for review
```
- All steps can be automated via Servius on OpenClaw
- Human review before publish (recommended)
- Cost: Same as Option B

---

## 7. API Key Requirements

| Service | Key Name | Where to Get |
|---------|----------|--------------|
| Fish Audio | `FISH_API_KEY` | fish.audio → Account → API |
| HeyGen | `HEYGEN_API_KEY` | heygen.com → Account → API Key |
| D-ID | `DID_API_KEY` | d-id.com → Account → Generate API Key |
| ElevenLabs (alt) | `ELEVENLABS_API_KEY` | elevenlabs.io → Profile → API Key |

---

## Sources
- Fish Audio developer page: https://fish.audio/developers/
- Fish Audio pricing (live): https://fish.audio/developers/ (API Pricing section)
- HeyGen pricing: https://www.heygen.com/pricing
- D-ID developer docs: https://docs.d-id.com/reference/get-started
- D-ID pricing FAQ: https://www.d-id.com/pricing/studio/
- DeepReel pricing: https://deepreel.com/pricing
- VideoAI.me platform comparison: https://videoai.me/blog/d-id-vs-heygen-vs-synthesia-vs-colossyan-comparison-2026
