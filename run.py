#!/usr/bin/env python3
"""
Intelli-Credit — Local Development Launcher
Starts FastAPI backend + React frontend (Vite dev server) together.
Press Ctrl+C to stop both.
"""

import subprocess
import sys
import os
import time
import signal
import threading
from pathlib import Path

BASE_DIR = Path(__file__).parent
BACKEND_DIR = BASE_DIR / "backend"
FRONTEND_DIR = BASE_DIR / "frontend"


def stream_output(proc, prefix, color_code):
    """Stream subprocess output with colour prefix."""
    for line in iter(proc.stdout.readline, b""):
        text = line.decode("utf-8", errors="replace").rstrip()
        print(f"\033[{color_code}m[{prefix}]\033[0m {text}", flush=True)


def check_env():
    env_file = BASE_DIR / ".env"
    if not env_file.exists():
        example = BASE_DIR / ".env.example"
        print("\033[33m[WARN] .env not found. Copying from .env.example...\033[0m")
        import shutil
        shutil.copy(example, env_file)
        print("\033[33m[WARN] Please set your API keys in .env before analyzing real documents.\033[0m")


def start_backend():
    print("\033[36m[BACKEND] Starting FastAPI on http://localhost:8000 ...\033[0m")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BACKEND_DIR)
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0",
         "--port", "8000", "--reload", "--log-level", "info"],
        cwd=str(BACKEND_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
    )
    t = threading.Thread(target=stream_output, args=(proc, "API", "36"), daemon=True)
    t.start()
    return proc


def start_frontend():
    if not (FRONTEND_DIR / "node_modules").exists():
        print("\033[35m[FRONTEND] Installing npm deps (first run)...\033[0m")
        subprocess.run(["npm", "install"], cwd=str(FRONTEND_DIR), check=True)

    print("\033[35m[FRONTEND] Starting Vite dev server on http://localhost:3000 ...\033[0m")
    proc = subprocess.Popen(
        ["npm", "run", "dev", "--", "--port", "3000", "--host"],
        cwd=str(FRONTEND_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=(sys.platform == "win32"),
    )
    t = threading.Thread(target=stream_output, args=(proc, "UI", "35"), daemon=True)
    t.start()
    return proc


def main():
    check_env()

    # Load .env
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")

    procs = []
    try:
        backend = start_backend()
        procs.append(backend)
        time.sleep(2)  # give API a moment to bind

        frontend = start_frontend()
        procs.append(frontend)

        print()
        print("\033[32m" + "─" * 60 + "\033[0m")
        print("\033[32m  ✅  Intelli-Credit is running!\033[0m")
        print("\033[32m  🌐  Frontend : http://localhost:3000\033[0m")
        print("\033[32m  🔌  API Docs : http://localhost:8000/docs\033[0m")
        print("\033[32m  📦  Qdrant   : http://localhost:6333/dashboard\033[0m")
        print("\033[32m" + "─" * 60 + "\033[0m")
        print("  Press Ctrl+C to stop all services.")
        print()

        # Wait for either process to exit
        while all(p.poll() is None for p in procs):
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\033[33m[INFO] Shutting down...\033[0m")
    finally:
        for p in procs:
            if p.poll() is None:
                p.terminate()
        for p in procs:
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()
        print("\033[33m[INFO] All services stopped.\033[0m")


if __name__ == "__main__":
    main()
