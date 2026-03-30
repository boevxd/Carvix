"""
Carvix — Запуск всех серверов одной командой
  python start_all.py

Запускает:
  1. FastAPI API сервер  → http://localhost:8000  (синхронизация с БД)
  2. Next.js веб-сайт   → http://localhost:3000  (веб-интерфейс)

PyQt6 приложение запускается отдельно: python carvix_app.py
"""

import subprocess
import sys
import os
import time
import signal
import threading

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_DIR = os.path.join(BASE_DIR, "html_s")

CYAN  = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED   = "\033[91m"
RESET = "\033[0m"
BOLD  = "\033[1m"

processes = []


def log(prefix: str, color: str, line: str):
    print(f"{color}[{prefix}]{RESET} {line}", flush=True)


def stream_output(proc, prefix: str, color: str):
    for line in iter(proc.stdout.readline, b""):
        log(prefix, color, line.decode("utf-8", errors="replace").rstrip())


def start_api():
    log("API", CYAN, "Запуск FastAPI сервера на http://localhost:8000 ...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api_server:app",
         "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd=BASE_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    processes.append(proc)
    t = threading.Thread(target=stream_output, args=(proc, "API", CYAN), daemon=True)
    t.start()
    return proc


def start_web():
    log("WEB", GREEN, "Запуск Next.js сайта на http://localhost:3000 ...")
    npm = "npm.cmd" if sys.platform == "win32" else "npm"
    proc = subprocess.Popen(
        [npm, "run", "dev"],
        cwd=HTML_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    processes.append(proc)
    t = threading.Thread(target=stream_output, args=(proc, "WEB", GREEN), daemon=True)
    t.start()
    return proc


def shutdown(sig=None, frame=None):
    print(f"\n{YELLOW}Остановка серверов...{RESET}")
    for p in processes:
        try:
            p.terminate()
        except Exception:
            pass
    time.sleep(1)
    for p in processes:
        try:
            p.kill()
        except Exception:
            pass
    print(f"{RED}Серверы остановлены.{RESET}")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    print(f"""
{BOLD}{CYAN}╔══════════════════════════════════════╗
║        CARVIX — Запуск системы       ║
╚══════════════════════════════════════╝{RESET}

  {CYAN}API сервер  {RESET}→ http://localhost:8000
  {CYAN}Документация{RESET}→ http://localhost:8000/docs
  {GREEN}Веб-сайт    {RESET}→ http://localhost:3000
  {YELLOW}Приложение  {RESET}→ python carvix_app.py

  {BOLD}Ctrl+C{RESET} для остановки
""")

    api_proc = start_api()
    time.sleep(2)   # даём API подняться первым
    web_proc = start_web()

    try:
        while True:
            if api_proc.poll() is not None:
                log("API", RED, f"АВАРИЙНОЕ завершение (код {api_proc.returncode})")
            if web_proc.poll() is not None:
                log("WEB", RED, f"АВАРИЙНОЕ завершение (код {web_proc.returncode})")
            time.sleep(5)
    except KeyboardInterrupt:
        shutdown()
