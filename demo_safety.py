"""Small safety guards for club demo apps (no secrets, mock-first)."""

from __future__ import annotations

import os
from pathlib import Path


def is_streamlit_cloud() -> bool:
    """Best-effort detection of Streamlit Community Cloud."""
    if os.environ.get('IS_STREAMLIT_CLOUD', '').strip().lower() in {'1', 'true', 'yes', 'on'}:
        return True
    # Community Cloud clones the app under /mount/src
    if Path('/mount/src').exists():
        return True
    return False


def allow_host_scan() -> bool:
    """
    Live OS introspection (passwd, netstat, directory walks) is OFF by default.
    Set ALLOW_HOST_SCAN=1 only on a machine you own and intend to probe.
    """
    return os.environ.get('ALLOW_HOST_SCAN', '').strip().lower() in {'1', 'true', 'yes', 'on'}


def allow_disk_persistence() -> bool:
    """
    JSON save/load against the working directory is for local/dev only.
    Disabled on Streamlit Cloud; override with ALLOW_DISK_PERSIST=1 if needed.
    """
    override = os.environ.get('ALLOW_DISK_PERSIST', '').strip().lower()
    if override in {'1', 'true', 'yes', 'on'}:
        return True
    if override in {'0', 'false', 'no', 'off'}:
        return False
    return not is_streamlit_cloud()
