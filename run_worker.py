"""
run_worker.py — Windows-safe ARQ worker launcher
Run with:  python run_worker.py
"""
import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from arq import run_worker
from processor import WorkerSettings

if __name__ == "__main__":
    run_worker(WorkerSettings)