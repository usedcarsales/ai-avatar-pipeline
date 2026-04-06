"""Master orchestrator — chains pipeline modules with business logic.

Handles approval gates, cost tracking, content scheduling, and
platform-specific optimizations.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from src.config import Config
from src.pipeline import AvatarPipeline, PipelineError

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Cost tracking
# ---------------------------------------------------------------------------

@dataclass
class CostEntry:
    """Single cost event."""
    timestamp: str
    service: str
    operation: str
    amount_usd: float
    metadata: dict[str, Any] = field(default_factory=dict)


class CostTracker:
    """Track per-video and cumulative API spend.

    Persists to a JSON-lines file so we never lose cost data.
    """

    # Average costs per call (HeyGen Creator plan, Fish Audio Pro)
    COST_TABLE: dict[str, float] = {
        "heygen_video": 0.50,       # ~$0.50/min of video on Creator plan
        "fish_tts": 0.02,           # ~$0.02 per TTS call (short script)
        "heygen_upload": 0.0,       # asset upload is free
    }

    def __init__(self, log_path: str | Path = "output/costs.jsonl") -> None:
        self._path = Path(log_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._entries: list[CostEntry] = []
        self._budget_usd: float = 35.0  # monthly budget

    @property
    def total_usd(self) -> float:
        return sum(e.amount_usd for e in self._entries)

    @property
    def budget_remaining(self) -> float:
        return self._budget_usd - self.total_usd

    def set_budget(self, amount: float) -> None:
        self._budget_usd = amount

    def record(self, service: str, operation: str, amount: float | None = None, **meta: Any) -> CostEntry:
        cost = amount if amount is not None else self.COST_TABLE.get(operation, 0.0)
        entry = CostEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            service=service,
            operation=operation,
            amount_usd=cost,
            metadata=meta,
        )
        self._entries.append(entry)
        with self._path.open("a") as f:
            f.write(json.dumps(entry.__dict__) + "\n")
        logger.info("Cost: $%.4f (%s/%s) — total: $%.2f / $%.2f budget",
                     cost, service, operation, self.total_usd, self._budget_usd)
        return entry

    def check_budget(self, estimated_cost: float = 0.0) -> bool:
        """Return True if estimated cost fits within remaining budget."""
        return (self.total_usd + estimated_cost) <= self._budget_usd


# ---------------------------------------------------------------------------
# Approval gate
# ---------------------------------------------------------------------------

class ApprovalRequired(Exception):
    """Raised when a job needs operator approval before proceeding."""


@dataclass
class Job:
    """A single video generation job with metadata and approval state."""
    job_id: str
    script: str
    avatar_id: str | None = None
    voice_source: Literal["heygen", "fish"] = "heygen"
    voice_id: str | None = None
    platform: str = "youtube"         # youtube | tiktok | instagram
    approved: bool = False
    output_path: str | None = None
    status: str = "pending"           # pending | approved | running | done | failed
    cost_usd: float = 0.0
    error: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: str | None = None


# ---------------------------------------------------------------------------
# Master Orchestrator
# ---------------------------------------------------------------------------

class Orchestrator:
    """Master pipeline controller with business logic.

    Features:
    - Approval gates before expensive API calls
    - Cost tracking and budget enforcement
    - Platform-specific output settings
    - Failure recovery (status tracking per job)
    - Job queue with persist/resume capability
    """

    PLATFORM_SETTINGS: dict[str, dict[str, int]] = {
        "youtube":   {"width": 1920, "height": 1080},
        "tiktok":    {"width": 1080, "height": 1920},
        "instagram": {"width": 1080, "height": 1080},
        "shorts":    {"width": 1080, "height": 1920},
    }

    def __init__(
        self,
        config: Config | None = None,
        require_approval: bool = True,
        budget_usd: float = 35.0,
        output_dir: str = "output",
    ) -> None:
        self.config = config or Config.from_env()
        self.pipeline = AvatarPipeline(self.config)
        self.costs = CostTracker(f"{output_dir}/costs.jsonl")
        self.costs.set_budget(budget_usd)
        self.require_approval = require_approval
        self.output_dir = Path(output_dir)
        self._jobs: dict[str, Job] = {}
        self._job_log = self.output_dir / "jobs.jsonl"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # -- Job management -----------------------------------------------------

    def create_job(
        self,
        script: str,
        *,
        job_id: str | None = None,
        avatar_id: str | None = None,
        voice_source: Literal["heygen", "fish"] = "heygen",
        voice_id: str | None = None,
        platform: str = "youtube",
    ) -> Job:
        """Create and queue a new video job."""
        jid = job_id or f"job_{int(time.time() * 1000)}"
        job = Job(
            job_id=jid,
            script=script,
            avatar_id=avatar_id,
            voice_source=voice_source,
            voice_id=voice_id,
            platform=platform,
        )
        self._jobs[jid] = job
        self._persist_job(job)
        logger.info("Job created: %s (platform=%s)", jid, platform)
        return job

    def approve_job(self, job_id: str) -> Job:
        """Mark a job as approved for execution."""
        job = self._jobs[job_id]
        job.approved = True
        job.status = "approved"
        self._persist_job(job)
        logger.info("Job approved: %s", job_id)
        return job

    async def execute_job(self, job_id: str) -> Job:
        """Execute a single job through the pipeline.

        Enforces approval gate and budget check before calling APIs.
        """
        job = self._jobs[job_id]

        # Approval gate
        if self.require_approval and not job.approved:
            raise ApprovalRequired(f"Job {job_id} requires approval before execution")

        # Budget check
        est_cost = self.costs.COST_TABLE.get("heygen_video", 0.50)
        if job.voice_source == "fish":
            est_cost += self.costs.COST_TABLE.get("fish_tts", 0.02)
        if not self.costs.check_budget(est_cost):
            job.status = "failed"
            job.error = f"Budget exceeded (remaining: ${self.costs.budget_remaining:.2f})"
            self._persist_job(job)
            raise PipelineError(job.error)

        # Platform-specific dimensions
        dims = self.PLATFORM_SETTINGS.get(job.platform, self.PLATFORM_SETTINGS["youtube"])
        self.config.video_width = dims["width"]
        self.config.video_height = dims["height"]

        # Output path
        out_path = self.output_dir / f"{job.job_id}.mp4"
        job.output_path = str(out_path)
        job.status = "running"
        self._persist_job(job)

        try:
            result = await self.pipeline.run(
                script=job.script,
                avatar_id=job.avatar_id,
                output_path=out_path,
                voice_source=job.voice_source,
                voice_id=job.voice_id,
            )
            # Record costs
            self.costs.record("heygen", "heygen_video", script_len=len(job.script))
            if job.voice_source == "fish":
                self.costs.record("fish", "fish_tts", script_len=len(job.script))

            job.cost_usd = est_cost
            job.status = "done"
            job.completed_at = datetime.now(timezone.utc).isoformat()
            self._persist_job(job)
            logger.info("Job complete: %s → %s ($%.2f)", job_id, result, job.cost_usd)
            return job

        except Exception as exc:
            job.status = "failed"
            job.error = str(exc)
            self._persist_job(job)
            logger.error("Job failed: %s — %s", job_id, exc)
            raise

    async def run_approved_jobs(self) -> list[Job]:
        """Execute all approved (not yet run) jobs in queue order."""
        results = []
        for job in self._jobs.values():
            if job.status == "approved":
                try:
                    await self.execute_job(job.job_id)
                except Exception:
                    pass  # already logged and persisted
                results.append(job)
        return results

    def get_status(self) -> dict[str, Any]:
        """Return a summary of all jobs and budget."""
        by_status: dict[str, int] = {}
        for j in self._jobs.values():
            by_status[j.status] = by_status.get(j.status, 0) + 1
        return {
            "total_jobs": len(self._jobs),
            "by_status": by_status,
            "total_cost_usd": round(self.costs.total_usd, 2),
            "budget_remaining_usd": round(self.costs.budget_remaining, 2),
            "budget_usd": self.costs._budget_usd,
        }

    def _persist_job(self, job: Job) -> None:
        """Append job state to the jobs log file."""
        with self._job_log.open("a") as f:
            f.write(json.dumps(job.__dict__) + "\n")
