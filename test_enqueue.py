"""
test_enqueue.py — enqueue a job straight onto the ARQ/Redis queue, bypassing
WhatsApp + Meta. Hits the SAME worker entrypoint (process_message) a real webhook
would, so it exercises the full pipeline: dedup -> Gemini -> Supabase -> reply.

USAGE (PowerShell, from project root, venv active):
    python test_enqueue.py "Spent 500 on lunch"
    python test_enqueue.py "Maine Rs 50 ki chai li thi"
    python test_enqueue.py "balance"

    # Force a specific wamid (e.g. to TEST dedup by sending the same one twice):
    python test_enqueue.py "Spent 600 on books" fixed-dedup-001

    # Override the recipient too (3rd arg), if you ever need a different number:
    python test_enqueue.py "50 chai" auto 923260467717

ARGS:
    1) text     (required) the message body to process
    2) wamid    (optional) message id. Omit or pass "auto" to generate a unique
                one each run (so the dedup gate never trips by accident).
    3) to       (optional) recipient phone in intl format. Defaults to DEFAULT_TO.
"""
import asyncio
import sys
import os
import uuid
import datetime
from urllib.parse import urlparse

from dotenv import load_dotenv
from arq import create_pool
from arq.connections import RedisSettings

# Windows: selector loop policy MUST be set before arq creates the Redis pool,
# or the rediss:// TLS handshake to Upstash breaks. Harmless on Linux.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

load_dotenv()

# Your WhatsApp number (an allowed test recipient on the app). Change if needed.
DEFAULT_TO = "923260467717"


def _redis_settings() -> RedisSettings:
    """Parse rediss:// Upstash URL into ARQ RedisSettings (TLS on)."""
    u = urlparse(os.getenv("REDIS_URL"))
    return RedisSettings(
        host=u.hostname, port=u.port or 6379,
        password=u.password, ssl=True,
    )


def _parse_args(argv: list[str]) -> tuple[str, str, str]:
    if len(argv) < 2 or not argv[1].strip():
        print('Usage: python test_enqueue.py "<message text>" [wamid|auto] [to]')
        sys.exit(1)

    text = argv[1]
    wamid_arg = argv[2] if len(argv) >= 3 else "auto"
    to = argv[3] if len(argv) >= 4 else DEFAULT_TO

    if wamid_arg == "auto":
        # Unique per run so the worker's _wamid_seen() dedup gate never trips
        # accidentally. Timestamp prefix keeps them sortable/readable in Supabase.
        stamp = datetime.datetime.now().strftime("%H%M%S")
        wamid = f"test-{stamp}-{uuid.uuid4().hex[:6]}"
    else:
        wamid = wamid_arg  # explicit -> deterministic, for dedup tests

    return text, wamid, to


async def main() -> None:
    text, wamid, to = _parse_args(sys.argv)

    pool = await create_pool(_redis_settings())
    try:
        job = await pool.enqueue_job("process_message", to, wamid, text=text)
        if job:
            print(f"ENQUEUED  wamid={wamid}  to={to}  text={text!r}")
            print(f"  job_id={job.job_id}")
            print("  Watch the worker terminal — it should pick this up.")
        else:
            # enqueue_job returns None if a job with this id already exists in the
            # queue (ARQ-level dedup by job id). Not the same as your DB dedup.
            print(f"NOT ENQUEUED (None) — a job for wamid={wamid} may already be "
                  f"queued/in-flight. Try a fresh wamid (omit the 2nd arg).")
    finally:
        await pool.aclose()


if __name__ == "__main__":
    asyncio.run(main())