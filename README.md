# AI Avatar Video Pipeline

Automated video production pipeline that turns a topic or script into a finished AI avatar video using Fish Audio (TTS) + HeyGen (avatar rendering).

Built by [Particulate LLC](https://particulate.ai).

## Stack

| Component | Service | Cost |
|-----------|---------|------|
| Voice / TTS | Fish Audio API | ~$0.09/video |
| Avatar Video | HeyGen Creator | $29/mo |
| Script Generation | Claude (Anthropic) | ~$0.01/video |
| **Total** | | **~$32/mo** |

30 videos/month = 95%+ gross margin at service pricing.

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/usedcarsales/ai-avatar-pipeline.git
cd ai-avatar-pipeline
pip install -r requirements.txt

# 2. Configure API keys
cp .env.example .env
# Edit .env with your HEYGEN_API_KEY (required) and FISH_API_KEY (optional)

# 3. List available avatars
python -m examples.list_available_avatars

# 4. Generate a video
python -m examples.generate_sample_video
```

## Architecture

```
Script (text) ─→ Voice Layer ─→ Avatar Layer ─→ .mp4 output
                  │                │
                  ├─ HeyGen TTS    └─ HeyGen avatar rendering
                  └─ Fish Audio TTS (custom voices)
```

**Two pipeline modes:**

- **Option A — HeyGen only** (`voice_source="heygen"`): Simplest path. HeyGen handles both voice synthesis and avatar rendering.
- **Option B — Fish Audio + HeyGen** (`voice_source="fish"`): Use Fish Audio for custom/cloned voices, then feed audio into HeyGen for avatar lip-sync.

## Usage

```python
import asyncio
from src.pipeline import AvatarPipeline
from src.config import Config

async def main():
    config = Config.from_env()
    pipeline = AvatarPipeline(config)

    # Option A: HeyGen handles voice
    await pipeline.run(
        script="Hello from Particulate LLC!",
        avatar_id="your_avatar_id",
        output_path="output/video.mp4",
    )

    # Option B: Fish Audio custom voice
    await pipeline.run(
        script="Hello with a custom voice!",
        avatar_id="your_avatar_id",
        output_path="output/custom_voice.mp4",
        voice_source="fish",
        voice_id="your_fish_reference_id",
    )

asyncio.run(main())
```

## Project Structure

```
src/
  config.py             # Environment variable loading
  heygen_client.py      # HeyGen API wrapper (async, retry, polling)
  fishaudio_client.py   # Fish Audio API wrapper (TTS, voice cloning)
  pipeline.py           # End-to-end orchestrator
tests/
  test_heygen_client.py    # Unit tests (mocked API calls)
  test_fishaudio_client.py # Unit tests (mocked API calls)
  test_pipeline.py         # Integration tests (live tests skipped by default)
examples/
  generate_sample_video.py   # Generate a sample video
  list_available_avatars.py  # Print available HeyGen avatars/voices
research/                    # Phase 1 research docs
```

## Running Tests

```bash
# Unit tests (no API keys needed)
pytest tests/

# Live integration tests (requires API keys in .env)
RUN_LIVE_TESTS=1 pytest tests/test_pipeline.py -v
```

## API Keys

### HeyGen
1. Sign up at https://www.heygen.com/ (Creator plan $29/mo)
2. Go to https://app.heygen.com/avatar?nav=API
3. Generate API key and add to `.env`

### Fish Audio
1. Sign up at https://fish.audio/
2. Go to Account → API Keys
3. Create a new key and add to `.env`

## Research

See the [`research/`](./research/) folder for Phase 1 findings:
- Target audience analysis
- Competitor analysis (HeyGen vs Synthesia vs D-ID vs DeepReel)
- Technical requirements & API docs
- Content strategy framework

## Roadmap

- [x] Phase 1: Research & architecture
- [x] Phase 2: Core pipeline modules (HeyGen + Fish Audio clients)
- [ ] Phase 3: Content engine & batch production
- [ ] Phase 4: Analytics & multi-brand expansion

## License

Proprietary — Particulate LLC
