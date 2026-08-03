#!/usr/bin/env python3
"""Ping Streamlit Community Cloud apps to reset the idle sleep timer."""

from __future__ import annotations

import concurrent.futures
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

URL_FILE = Path(__file__).resolve().parent / "streamlit_urls.txt"
TIMEOUT_SEC = 90
WORKERS = 8


def load_urls() -> list[str]:
    lines = URL_FILE.read_text(encoding="utf-8").splitlines()
    return [
        line.strip()
        for line in lines
        if line.strip() and not line.strip().startswith("#")
    ]


def ping(url: str) -> tuple[str, str, float]:
    started = time.perf_counter()
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "rungrc-raleigh-keepalive/1.0"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
            status = f"HTTP {resp.status}"
    except urllib.error.HTTPError as exc:
        # 5xx during cold start still usually counts as a visit.
        status = f"HTTP {exc.code}"
    except Exception as exc:  # noqa: BLE001
        status = f"ERR {type(exc).__name__}: {exc}"
    elapsed = time.perf_counter() - started
    return url, status, elapsed


def main() -> int:
    urls = load_urls()
    if not urls:
        print(f"No URLs in {URL_FILE}", file=sys.stderr)
        return 1

    print(f"Pinging {len(urls)} Streamlit apps…")
    ok = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = [pool.submit(ping, url) for url in urls]
        for fut in concurrent.futures.as_completed(futures):
            url, status, elapsed = fut.result()
            host = url.replace("https://", "").rstrip("/")
            print(f"{status:28} {elapsed:5.1f}s  {host}")
            if status.startswith("HTTP"):
                ok += 1

    print(f"Done: {ok}/{len(urls)} responded with HTTP")
    # Don't fail the workflow on a couple of sleepy apps —
    # the request itself is what resets / wakes them.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
