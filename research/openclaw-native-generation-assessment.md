# OpenClaw v2026.4.5 — Native Generation Assessment
## AI Avatar Pipeline Architecture Decision

**Date:** April 6, 2026 | **Researcher:** Servius

---

## VERDICT: Do NOT pivot. Keep HeyGen + Fish Audio. Optimize with native where it helps.

**TL;DR:** OpenClaw's new native video/image generation tools are text-to-video (B-roll), NOT avatar lip-sync. The core feature of our pipeline — a consistent presenter talking to a script — does not exist in any native provider. We save $5-21/month by using FAL's existing access for B-roll instead of a separate Kling subscription.

---

## 1. What's New in OpenClaw 2026.4.5

Per official release (April 6, 2026, blockchain.news):
- ✅ Built-in video generation (multi-provider, `video_generate` tool)
- ✅ Built-in image generation (multi-provider, `image_generate` tool)
- ✅ Music generation via `/dreaming` (now GA)
- ✅ Structured task progress, prompt-cache reuse, 12 new UI languages
- ❌ NO lip-sync avatar generation
- ❌ NO voice cloning
- ❌ NO script → talking head pipeline

---

## 2. Provider Inventory (Live from This Machine)

### Image Generation
| Provider | Configured | Models |
|---------|------------|--------|
| **fal** | **✅ YES (FAL_KEY)** | flux/dev, flux/dev/image-to-image |
| google | ❌ Need GEMINI_API_KEY | gemini-3.1-flash-image-preview |
| minimax | ❌ Need MINIMAX_API_KEY | image-01 |
| openai | ❌ Need OPENAI_API_KEY | gpt-image-1 |
| vydra | ❌ Need VYDRA_API_KEY | grok-imagine |

### Video Generation
| Provider | Configured | Models | Max Duration |
|---------|------------|--------|-------------|
| **fal** | **✅ YES (FAL_KEY)** | **kling-video/v2.1**, minimax/video-01-live, wan/v2.2 | varies |
| google | ❌ Need GEMINI_API_KEY | **veo-3.1** (fast/std/lite), veo-3.0, veo-2.0 | 8s |
| minimax | ❌ Need MINIMAX_API_KEY | MiniMax-Hailuo-2.3, I2V-01-Director | 10s |
| openai | ❌ Need OPENAI_API_KEY | **sora-2**, sora-2-pro | 12s |
| runway | ❌ Need RUNWAYML_API_SECRET | gen4.5, gen4_turbo, veo3.1 | 10s |
| together | ❌ Need TOGETHER_API_KEY | Wan2.2, Kling-2.1-Master | 12s |
| alibaba | ❌ Need MODELSTUDIO_API_KEY | wan2.6/2.7 | 10s |
| byteplus | ❌ Need BYTEPLUS_API_KEY | seedance-1-0/1-5-pro | 12s |

### TTS / Voice
| Provider | Configured | Cost | Quality |
|---------|------------|------|---------|
| **Microsoft Edge TTS** | **✅ FREE, built-in, no key** | $0 | Good neural voices, 400+, 100+ languages |
| ElevenLabs | ❌ Need ELEVENLABS_API_KEY | $5-22/mo | Excellent |
| MiniMax TTS | ❌ Need MINIMAX_API_KEY | varies | Good |
| OpenAI TTS | ❌ Need OPENAI_API_KEY | pay-per-use | Very good |

**Note on "Sora-2":** The `sora-2` in OpenClaw's provider list is NOT the "Sora" shut down in March 2026. This appears to be a new OpenAI video API iteration. Status unclear without OPENAI_API_KEY to test.

---

## 3. Live Test Results

### Test 1: FAL FLUX/dev Image (avatar headshot)
- Generated in ~15 seconds ✅
- Quality: Corporate styling ✅, composition ✅, but **BLURRY** — facial features indistinct
- **FAIL for avatar reference** — face landmarks too soft for lip-sync rigging
- OK for thumbnails with text overlay

### Test 2: FAL Kling v2.1 Video (talking presenter)
- Generated successfully: **5.0s, 1920×1080, 24fps, H.264, 4.39MB** ✅
- Scene looks natural with person in professional setting ✅
- **No lip-sync to script** ❌
- **Different person each generation** ❌ (no character continuity)
- → B-roll quality, NOT avatar replacement

### Test 3: FAL MiniMax video
- Generated: 5.6s, 1280×720, 545KB
- Lower quality than Kling, same limitations

---

## 4. The Critical Gap

None of OpenClaw's native providers do lip-sync. This is a fundamental product difference:

| Capability | OpenClaw Native | HeyGen |
|-----------|-----------------|--------|
| Generate image of person | ✅ | ✅ |
| Generate video of person | ✅ | ✅ |
| Consistent avatar (same face every time) | ❌ | ✅ |
| Lip-sync to audio/script | ❌ | ✅ |
| Script → talking head | ❌ | ✅ |
| Voice cloning | ❌ | ✅ |

**Text-to-video ≠ Avatar video. These are different products.**

---

## 5. What Native Generation DOES Help With

### B-Roll (Immediate Win)
We were planning a $6-22/mo Kling subscription. **We can use Kling v2.1 via FAL which we already have paid for.** Drop the separate Kling subscription.

### Microsoft TTS (Free Voice)
Built-in, no API key, 400+ neural voices, 100+ languages, 24kHz. 
- For faceless content (no avatar): use Microsoft TTS instead of Fish Audio
- Not usable for voice cloning (use Fish Audio for that)

### Thumbnails
FLUX generates acceptable thumbnail images (professional look, may be slightly soft but text overlay hides it).

### Music (Future)
`/dreaming` GA in 2026.4.5 — background music for videos without licensing fees. Need to test quality.

---

## 6. Updated Cost Model

| Service | Before | After | What Changed |
|---------|--------|-------|-------------|
| HeyGen Creator | $29 | $29 | KEEP — irreplaceable |
| Fish Audio (avatar voice) | $3 | $2 | Slight volume reduction |
| Kling subscription | $6-22 | **$0** | Replaced by FAL (already have key) |
| FAL pay-per-use (B-roll) | $3 | $3 | No change (already paying) |
| Microsoft TTS | $0 | $0 | Free, now using it |
| **Total** | **$41-57** | **~$34** | **Saves $7-23/month** |

---

## 7. Future Provider Unlock Recommendations

When scaling, add these keys to unlock better options:

1. **GEMINI_API_KEY** → Veo 3.1 (Google's best, audio support, 8s clips) — best next add
2. **TOGETHER_API_KEY** → Kling-2.1-Master + other models cheaply
3. **RUNWAYML_API_SECRET** → Gen4.5 for premium hero shots (expensive, use sparingly)
4. **OPENAI_API_KEY** → gpt-image-1 (best image quality) + Sora-2 testing

---

## Sources
- OpenClaw 2026.4.5 release: blockchain.news (April 6, 2026)
- Live provider lists from running OpenClaw instance
- TTS docs: openclaw/docs/tts.md
- Live tests: FAL/flux image (blurry), FAL/kling-v2.1 (5s 1080p, no lip-sync), FAL/minimax (5.6s 720p)
