# AI Video Automation Research — Faceless YouTube/TikTok Pipeline
## Particulate LLC / Layered Up

**Date:** April 6, 2026  
**Researcher:** Servius  
**Project:** Faceless content automation pipeline

---

## Executive Summary

Faceless AI video channels are a proven revenue model in 2026. Top channels earn $5K-$50K+/month; realistic for a well-positioned new channel is $500-$3,000/month within 6-12 months. The total automation stack costs $29-$60/month. At 30 videos/month in a finance/tech/education niche, projected AdSense revenue is $450-$2,700/month (break-even ~month 3-6 assuming consistent publishing).

**Recommended stack for Particulate LLC:**
- Voice: **ElevenLabs Creator ($22/mo)** — best quality, 100K chars/month, voice cloning
- Video: **HeyGen Creator ($29/mo)** — already integrated in ai-avatar-pipeline
- Text-to-video B-roll: **Kling AI (~$10-22/mo)** — best value for supplemental footage
- Total: ~$61/mo

---

## 1. AI Voice Services Comparison

### ElevenLabs
**Website:** elevenlabs.io  
**Status:** Industry leader for natural voice quality

| Plan | Price | Monthly Chars (Multilingual v2) | Extra Cost | Key Features |
|------|-------|--------------------------------|------------|--------------|
| Free | $0 | ~10 min | N/A | 10K credits, no commercial |
| Starter | $5/mo | ~30 min | — | 30K credits, commercial rights, voice cloning |
| **Creator** | **$22/mo** | **~100 min** | **~$0.30/min extra** | **100K credits, Pro voice cloning, 192kbps** |
| Pro | $99/mo | ~500 min | ~$0.24/min | High volume |

**API:** RESTful, Python/JS SDKs, excellent documentation  
**Voice cloning:** Instant cloning on Starter+; Professional cloning on Creator+  
**Quality:** Highest naturalness; best for faceless content where voice IS the channel  
**Languages:** 29+ languages natively  

**At 30 videos/month (avg 5 min each = 150 min):**
- Creator plan covers ~100 min → need ~50 min extra
- Extra cost: ~$15 → total ~$37/mo
- OR use Flash model (cheaper): 200 min included at Creator → no overages needed

**Best for:** Channels where voice quality is the differentiator; high-quality narration content

---

### Fish Audio
**Website:** fish.audio  
**Status:** Our existing integration, pay-as-you-go

| Model | Price | Notes |
|-------|-------|-------|
| S2 Pro | $15/million UTF-8 bytes | ~$0.09 per 1,000-word script |
| S1 | $15/million UTF-8 bytes | Same price, slightly lower quality |

**API:** REST + Python/JS SDKs (already integrated)  
**Voice cloning:** From 10 seconds of audio  
**Languages:** English, Japanese, Korean, Chinese, French, German, Arabic, Spanish  
**Community voices:** 2M+ voices available  

**At 30 videos/month (avg 1,000-word script each):**
- 30 scripts × ~6,000 bytes each = 180,000 bytes = $0.18 × 15/million = **$2.70/month**
- Extraordinarily cheap

**Best for:** High-volume production where quality is "good enough"; cost-sensitive operations  
**Weakness:** Fewer language options than ElevenLabs; emotion control limited

---

### Play.ht
**Website:** play.ht  
**Status:** ⚠️ DNS errors observed on April 6, 2026 — site appears down/troubled  

**Historical pricing (last known):** $29-$99/month  
**API:** Available  
**Verdict:** Avoid until service stability confirmed. Do not build dependency on Play.ht.

---

### LOVO AI (Genny)
**Website:** lovo.ai  
**Status:** Active, 2M+ users, includes video editor

| Plan | Price | Voice Gen | Voice Clones | Key Features |
|------|-------|-----------|--------------|--------------|
| Basic | $24/mo | 2 hrs/mo | 5 voices | 500+ voices, 100+ languages, commercial |
| **Pro** | **$48/mo** | **5 hrs/mo** | **Unlimited** | **+ multilingual, voice enhancer, AI script** |
| Pro+ | $75/mo | 20 hrs/mo | Unlimited | High volume teams |
| Enterprise | Custom | Custom | Custom | API access |

**Note:** API access is Enterprise-only at LOVO — this is a significant limitation for pipeline automation.

**Built-in video editor:** LOVO includes a video creation suite with stock media, AI script generator, and auto-subtitle — makes it a more complete "one-stop" platform.  
**Best for:** Creators who want an all-in-one solution without coding; not ideal for automated pipeline due to API limitations.

---

### Voice Service Comparison Matrix

| Service | Best Price Fit | Quality | API | Voice Cloning | Languages | Pipeline Automation |
|---------|---------------|---------|-----|---------------|-----------|---------------------|
| **ElevenLabs Creator** | $22/mo | ⭐⭐⭐⭐⭐ | ✅ Excellent | ✅ Pro cloning | 29+ | ✅ Easy |
| **Fish Audio** | ~$3/mo | ⭐⭐⭐⭐ | ✅ Excellent | ✅ 10-sec | 8 major | ✅ Already integrated |
| LOVO Pro | $48/mo | ⭐⭐⭐⭐ | ❌ Enterprise only | ✅ Unlimited | 100+ | ❌ No API access |
| Play.ht | ~~$29/mo~~ | ⭐⭐⭐⭐ | ✅ | ✅ | 900+ voices | ❌ Service down |

**Recommendation:** 
- **Budget route:** Fish Audio (~$3/mo) — already integrated, proven
- **Quality route:** ElevenLabs Creator ($22/mo) — best naturalness for face-of-channel voice
- **Do not use:** LOVO (no API), Play.ht (service issues)

---

## 2. Avatar/Video Services Beyond HeyGen (Already Covered)

See `competitor-analysis.md` for full breakdown. Key additions for faceless content context:

| Platform | Price | Best For Faceless | Notes |
|---------|-------|------------------|-------|
| **Synthesia Starter** | $22/mo | Training/educational | 10 min/mo limit |
| **D-ID Pro** | $29.99/mo | Photo-to-video narration | API-first, good for automation |
| **Colossyan Starter** | $19/mo | L&D/training style | 10 min/mo limit |
| **InVideo AI** | $25/mo | Template-assembled faceless | Not avatar-based but full video |

**InVideo AI** is particularly relevant for faceless content — it auto-assembles videos from scripts using AI voiceover + stock footage (no avatar needed). Produces YouTube-ready content without requiring avatar generation. Worth evaluating as a simpler alternative to the HeyGen pipeline for purely faceless (no face) content.

---

## 3. Text-to-Video (Sora-Style) Options

These generate novel video footage from text/image prompts — useful as B-roll, not as avatar replacements.

### Runway Gen-3 Alpha
**Price:** $12/mo (125 credits) to $76/mo (unlimited)  
**Max length:** 10 seconds per generation  
**Quality:** ⭐⭐⭐⭐⭐ — industry benchmark for visual fidelity  
**Camera control:** Yes — precise movement direction  
**Cost per second:** $0.24-$0.50  
**Best for:** Premium hero shots, cinematic B-roll, professional productions  
**Limitation:** 10-second clips; expensive for volume

### Kling AI
**Website:** kling.kuaishou.com  
**Price:** $5.99/mo (660 credits) to $21.99/mo (3,000 credits)  
**Max length:** **60 seconds** — longest single generation in market  
**Quality:** ⭐⭐⭐⭐ — excellent natural motion, good character consistency  
**Cost per second:** ~$0.09  
**Best for:** Longer B-roll segments, character scenes, establishing shots  
**Notable:** Face swap feature; globally available despite Chinese origin  
**Limitation:** Less camera control; queue times during peak

### Pika Labs
**Price:** $8/mo to $58/mo  
**Max length:** 4 seconds  
**Quality:** ⭐⭐⭐ — stylized, creative  
**Cost per second:** ~$0.15-0.25  
**Best for:** Quick social clips, style effects, budget experimentation  
**Limitation:** 4-second max makes it impractical for YouTube B-roll

### Luma Dream Machine
**Price:** $9.99/mo (120 generations) to $29.99/mo (400 generations)  
**Max length:** 5 seconds  
**Quality:** ⭐⭐⭐⭐ — cinematic look  
**Cost per second:** ~$0.17  
**Best for:** Stylized, dreamy aesthetic content

### ⚠️ IMPORTANT NOTE: Sora (OpenAI)
**Status: SHUT DOWN** as of March 2026  
"Sora was shut down by OpenAI in March 2026 due to unsustainable infrastructure costs." (ZSky.ai, March 2026)  
Do NOT include Sora in any pipeline planning.

### Can Text-to-Video Replace Avatar Services?

**Short answer: No — they serve different functions.**

| Function | Avatar (HeyGen) | Text-to-Video (Kling/Runway) |
|----------|-----------------|------------------------------|
| Consistent presenter/face | ✅ | ❌ (no continuity) |
| Script narration | ✅ | ❌ |
| Novel visual scenes | ❌ | ✅ |
| B-roll footage | ❌ | ✅ |
| Product demos | ✅ | ⚠️ (inconsistent) |
| Cost per minute | ~$2 | $9-30 |

**Best practice:** Use avatar (HeyGen) for presenter segments + Kling for B-roll inserts. Hybrid approach creates higher-quality videos without the $0.40/second Runway price.

---

## 4. Automated Content Calendar Workflow

### Full Pipeline: Topic → Script → Voice → Video → Upload

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: TOPIC RESEARCH (Automated with Servius)             │
│ - Keyword tools (TubeBuddy, VidIQ API, Google Trends)       │
│ - LLM analysis: "What topics in [niche] have high search    │
│   volume but low competition right now?"                    │
│ - Output: 30 approved topics/month                          │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: SCRIPT GENERATION (Claude/GPT via API)              │
│ - Input: Topic + niche guidelines + voice style             │
│ - Output: 800-1,500 word script (5-8 min video)             │
│ - Includes: Hook (0-30s), body, CTA, thumbnail keywords     │
│ - Human review: 5 min per script (check facts, tone)        │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: VOICE GENERATION (Fish Audio or ElevenLabs API)     │
│ - Input: Approved script + voice model ID                   │
│ - Output: narration.mp3                                     │
│ - Cost: $0.09 (Fish) or $0.22 (ElevenLabs) per video        │
│ - Time: 30 seconds via API                                  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: VIDEO GENERATION (Two approaches)                   │
│                                                             │
│ OPTION A (Avatar): HeyGen API                               │
│ - Avatar syncs lips to narration.mp3                        │
│ - Cost: ~$2/video, 2-5 min generation time                  │
│                                                             │
│ OPTION B (Pure Faceless): InVideo AI or stock footage       │
│ - Script → AI selects relevant stock clips                  │
│ - Narration plays over b-roll montage                       │
│ - Cost: ~$1/video (template-based)                          │
│                                                             │
│ OPTION C (Hybrid): Avatar intro + Kling B-roll              │
│ - Avatar segment (30s intro) via HeyGen                     │
│ - Body sections use Kling-generated B-roll                  │
│ - Highest quality; ~$3-5/video                              │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: POST-PRODUCTION (Automated)                         │
│ - Auto-captions (Fish Audio ASR: $0.36/hr or ElevenLabs)    │
│ - Thumbnail generation (DALL-E 3 or Stable Diffusion)       │
│ - Title/description/tags (Claude API)                       │
│ - Time: ~2 min automated + 3 min human review               │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 6: UPLOAD & SCHEDULE (YouTube Data API v3)             │
│ - Automated upload via OAuth2 + YouTube API                 │
│ - Schedule for optimal posting time (based on analytics)    │
│ - Cross-post: auto-clip to Shorts + TikTok                  │
│ - Notify operator via Discord (Servius)                     │
└─────────────────────────────────────────────────────────────┘
```

### Content Calendar Template (30 Videos/Month)

| Week | Videos | Format | Niche Pillar |
|------|--------|--------|--------------|
| Week 1 | 8 | 3 long-form (8 min), 5 Shorts (60s) | Core topic pillar |
| Week 2 | 7 | 2 long-form, 5 Shorts | Related subtopic |
| Week 3 | 8 | 3 long-form, 5 Shorts | Trending topic |
| Week 4 | 7 | 2 long-form, 5 Shorts | Evergreen / SEO |

**Operator time:** ~15-20 hours/month (topic approval, script review, final QC)  
**Automation handles:** Research, scripting, voice, video, captions, upload

---

## 5. Revenue Models

### YouTube AdSense

**Eligibility:** 1,000 subscribers + 4,000 watch hours (standard) OR 500 subscribers + 3,000 watch hours (Shorts monetization)

**CPM rates by niche (US viewers):**
| Niche | CPM | RPM (actual revenue/1K views) |
|-------|-----|-------------------------------|
| Finance / Investing | $12.25 | $8-10 |
| Digital Marketing | $12.41 | $8-10 |
| AI / Tech | $7.31 | $5-7 |
| Education | $9.89 | $6-8 |
| Lifestyle | $3.47 | $2-3 |
| Entertainment | ~$1.00 | $0.50-1 |

**Geographic CPM premium:** US/Australia/Canada views worth 3-5× more than global average

**Revenue projection at 30 videos/month (established channel):**

Assumptions: Finance/AI niche, 50% US audience, 3 months to initial momentum, RPM = $7

| Timeline | Monthly Views | Monthly AdSense |
|----------|--------------|-----------------|
| Month 1-3 | 0-5,000 | $0-35 |
| Month 4-6 | 5,000-20,000 | $35-140 |
| Month 7-12 | 20,000-100,000 | $140-700 |
| Year 2 | 100,000-500,000 | $700-3,500 |
| Year 3+ (scaled) | 500,000+ | $3,500-15,000 |

**Reality check from techmuni.dev (2025):** "Automated channels tend to perform well on quantity but inconsistently on depth. AI scripts can match the surface structure of strong videos yet often lack specific insights and personal perspectives." → Need human editorial voice to differentiate.

**Example real channels:**
- Motivational faceless channel: 0 → 500K subscribers in 12 months → **$12,000/month** (Clippie.ai)
- Finance explainer channels: $138,000-$388,000/month at scale (Daily Dose of Internet)
- Realistic new channel range: $500-$3,000/month by month 12

### TikTok Creator Fund / Creativity Program

- Pays $0.02-$0.04 per 1,000 views (US)
- TikTok Creativity Program (for 1-min+ videos): $0.40-$0.80 per 1,000 qualified views
- At 30 videos/month × average 10,000 views = 300,000 views = **$120-$240/month** (Creativity Program)
- Lower than YouTube AdSense but drives discovery and cross-channel growth

### Consulting Upsell

Our biggest differentiator: we don't just run channels — we can sell the pipeline as a service.

**Productized consulting:**
- "AI Channel Setup": $1,497 one-time → deliver working pipeline + first 10 videos
- "Done-For-You Monthly": $799-$1,499/month → we run the channel, they own it
- "AI Video Training": $297 → teach them our workflow

At 3 Done-For-You clients: **$2,400-$4,500/month**  
Combined with own channels: **$3,000-$7,500/month** by month 12

### Affiliate Marketing

High-RPM addition, especially for finance/tech niches:
- AI tool referrals (ElevenLabs, HeyGen affiliates): 20-30% recurring commission
- Software tools in niche: $20-200 per conversion
- Potential: $500-$2,000/month on an established channel

---

## 6. Competitor Analysis: Successful Faceless AI Channels

### Channel Archetypes That Work

**Archetype 1: AI/Tech News Explainers**
- Format: "5 AI tools that changed everything this week"
- Production: Pure stock footage + AI narration (no avatar)
- CPM: $7-12 (tech audience)
- Examples: Multiple 100K-500K subscriber channels

**Archetype 2: Finance/Investing Explainers**  
- Format: "Why [company] stock is going to [outcome]"
- Production: Charts + AI avatar presenter
- CPM: $8-15 (highest-value audience)
- Examples: Cash flow focused channels earning $5K-$20K/month

**Archetype 3: Productivity/Self-Improvement**
- Format: "10 habits of highly successful people"
- Production: Motivational stock footage + AI voiceover
- CPM: $5-8
- Risk: Saturated niche; need strong hook/differentiation

**Archetype 4: Niche News/Analysis**
- Format: Automotive industry news, crypto updates, etc.
- Production: Simple AI avatar (our HeyGen setup is perfect)
- CPM: Varies by niche ($3-15)
- **Best fit for Particulate LLC:** Automotive (BDC Closer synergy), AI business news, real estate

### What Separates Successful Channels from Failures

From techmuni.dev analysis (2025):

1. **Editorial positioning** — "Faceless" ≠ "identity-less." Need a clear niche voice, not generic AI content
2. **Retention engineering** — Hook in first 30 seconds is critical; AI scripts often fail here without human editing
3. **Consistency beats volume** — 3 quality videos/week > 7 mediocre videos/week
4. **SEO discipline** — Title/thumbnail optimization drives 80% of initial views
5. **Avoid copyright issues** — AI-assembled videos using stock footage can trigger ContentID; need proper licensing

### Competitive Opportunity: The BDC Closer / Automotive Niche

Our unique angle: We run BDC Closer, an AI automotive sales tool. This gives us authentic expertise to create:
- "AI in automotive sales" YouTube channel
- "Car dealership technology" explainers
- Automotive industry news

This niche has:
- High CPM (automotive advertisers pay $10-20+ CPM)
- Low AI content saturation (underserved)
- Built-in credibility from our actual product
- Consulting upsell opportunity (sell BDC Closer to dealers)

---

## 7. Recommended Stack for Particulate LLC

### Tier 1: Minimum Viable (Start Here)
**Monthly cost: ~$51**
- HeyGen Creator: $29/mo (already have this integrated)
- Fish Audio: ~$3/mo (already integrated, pay-as-you-go)
- Claude API for scripts: ~$5/mo (at 30 scripts × 1,000 tokens each)
- Kling AI: $5.99/mo (B-roll generation supplement)
- YouTube Data API: Free

**Output:** 30 avatar videos + supplemental B-roll, fully automated pipeline

### Tier 2: Quality Upgrade (Month 3+)
**Monthly cost: ~$80**
- Upgrade voice to ElevenLabs Creator: $22/mo
- Add HeyGen Pro ($99/mo) if volume demands OR keep Creator ($29/mo)
- Kling Standard: $21.99/mo (more credits for longer B-roll)
- Total: ~$73-143/mo depending on HeyGen tier

### Tier 3: Scale (Year 2)
**Monthly cost: ~$150-300**
- Multiple channels (automotive, AI business, lifestyle)
- Dedicated virtual assistant for QC ($300-500/mo from international VA)
- Runway: Add for premium hero shots when needed

---

## 8. Action Plan

### Month 1
- [ ] Choose niche (automotive/AI business recommended)
- [ ] Set up YouTube channel with brand identity
- [ ] Build automated script generation via Claude API
- [ ] Connect Fish Audio + HeyGen pipeline (ai-avatar-pipeline repo)
- [ ] Publish 8-10 videos, analyze what gets traction

### Month 2-3
- [ ] Double down on formats/topics that got views
- [ ] Implement auto-upload via YouTube Data API
- [ ] Add Kling B-roll inserts to increase production quality
- [ ] Reach 500 subscribers → apply for YouTube Monetization (new threshold)

### Month 4-6
- [ ] Monetization enabled → first AdSense checks
- [ ] Add affiliate links to relevant videos
- [ ] Begin consulting upsell to other businesses wanting similar channels
- [ ] Test TikTok cross-posting

### Month 7-12
- [ ] Scale to 30+ videos/month
- [ ] Add second channel in complementary niche
- [ ] Done-For-You channel service: $799-$1,499/mo per client
- [ ] Target: $3,000-$7,500/month combined income

---

## Sources
- ZSky.ai AI Video Generator Pricing 2026: https://zsky.ai/ai-video-generator-pricing-comparison.html
- Multic.com: Runway vs Kling vs Pika comparison: https://www.multic.com/guides/runway-vs-kling-vs-pika/
- ElevenLabs pricing (live, April 2026): https://elevenlabs.io/pricing
- LOVO AI pricing (live, April 2026): https://lovo.ai/pricing
- TechMuni.dev: AI YouTube Automation 2025 review: https://www.techmuni.dev/2025/11/ai-powered-faceless-youtube-automation.html
- YouGenie Blog: Faceless YouTube channel earnings: https://blog.yougenie.co/posts/faceless-youtube-channel-earnings
- Clippie.ai: How to make money from faceless AI videos: https://clippie.ai/blog/how-to-make-money-faceless-ai-videos-2025
- Fish Audio API docs: https://fish.audio/developers/
- ⚠️ Sora: Confirmed shut down March 2026 per ZSky.ai
- ⚠️ Play.ht: DNS errors April 6, 2026 — service appears down
