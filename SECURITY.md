# Security — AI Avatar Pipeline

## API Key Management
- **Never commit `.env` files.** The `.gitignore` excludes `.env` by default.
- Copy `.env.example` → `.env` and fill in your keys locally.
- Use `Config.redacted()` for logging — it masks API keys automatically.
- In production, use environment variables or a secrets manager (e.g., Render env vars).

## Input Validation
- Scripts are validated for emptiness and max length (10,000 chars) before API calls.
- Avatar/voice IDs are required and checked before submission.
- File paths for voice cloning are validated for existence.

## Rate Limiting & Retries
- Both HeyGen and Fish Audio clients implement exponential backoff.
- Rate limit responses (HTTP 429) are retried automatically up to `MAX_RETRIES`.
- Configurable via `MAX_RETRIES` and `BACKOFF_BASE` env vars.

## Network Security
- All API calls use HTTPS exclusively.
- Timeouts: 30s for HeyGen, 60s for Fish Audio (TTS requires more time).
- No credentials are logged — use `Config.redacted()` for debug output.

## Reporting Vulnerabilities
Contact the repository owner directly. Do not open public issues for security concerns.
