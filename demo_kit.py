"""Shared interaction helpers for Streamlit club demos (mechanics only)."""

from __future__ import annotations

from typing import Any, Optional

import pandas as pd
import streamlit as st

_SEED_KEY = "demo_kit_seed"

# Brownfield flavor — append beside existing greenfield samples, do not replace them
LEGACY_PLATFORMS = [
    {
        "name": "IBM i (AS/400 Power)",
        "short": "IBM i",
        "family": "IBM midrange",
        "examples": "QSYS, *ALLOBJ, QSECURITY, IFS",
    },
    {
        "name": "IBM Z (z/OS)",
        "short": "IBM Z",
        "family": "IBM mainframe",
        "examples": "RACF, CICS, DB2 for z/OS, IMS",
    },
    {
        "name": "AIX LPAR",
        "short": "AIX",
        "family": "UNIX",
        "examples": "LPAR, WPAR, adopted authority",
    },
    {
        "name": "JD Edwards World / EnterpriseOne",
        "short": "JD Edwards",
        "family": "ERP",
        "examples": "World programs, EnterpriseOne CNC, IFS shares",
    },
    {
        "name": "SAP ECC (on-prem)",
        "short": "SAP ECC",
        "family": "ERP",
        "examples": "SAP_ALL, SU01, ST01 traces",
    },
    {
        "name": "Oracle E-Business Suite",
        "short": "Oracle EBS",
        "family": "ERP",
        "examples": "APPS schema, Concurrent Manager",
    },
    {
        "name": "On-prem Active Directory",
        "short": "Windows AD",
        "family": "Microsoft estate",
        "examples": "Domain controllers, GPO, RDP bastion",
    },
]


def legacy_platform_names():
    return [p["short"] for p in LEGACY_PLATFORMS]


def ensure_seed(default: int = 42) -> int:
    """Return session sample-data seed, initializing if needed."""
    if _SEED_KEY not in st.session_state:
        st.session_state[_SEED_KEY] = int(default)
    return int(st.session_state[_SEED_KEY])


def bump_seed() -> int:
    """Advance seed so sample generators can reshuffle."""
    ensure_seed()
    st.session_state[_SEED_KEY] = int(st.session_state[_SEED_KEY]) + 1
    return int(st.session_state[_SEED_KEY])


def reset_seed(default: int = 42) -> int:
    st.session_state[_SEED_KEY] = int(default)
    return int(default)


def seed_controls(*, show_reset: bool = True, label: str = "Sample data") -> int:
    """Sidebar resample / reset buttons. Returns current seed."""
    st.subheader(label)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Resample", use_container_width=True):
            bump_seed()
            st.rerun()
    with c2:
        if show_reset and st.button("Reset", use_container_width=True):
            reset_seed()
            st.rerun()
    return ensure_seed()


def csv_download(
    df: pd.DataFrame,
    filename: str,
    *,
    label: str = "Download CSV",
    key: Optional[str] = None,
) -> None:
    """One-liner CSV download for the current filtered view."""
    if df is None or df.empty:
        st.caption("Nothing to export for the current filters.")
        return
    st.download_button(
        label=label,
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
        key=key,
        use_container_width=True,
    )


def autoload(key: str, factory) -> None:
    """Populate st.session_state[key] once if missing/empty so demos aren't blank on open."""
    cur = st.session_state.get(key)
    empty = cur is None or cur == [] or cur == {}
    if empty:
        st.session_state[key] = factory()


def issue_text(row: Any, *keys: str, default: str = "Review required") -> str:
    """Pull a human-readable issue string from common mock-data column names."""
    data = row if isinstance(row, dict) else row.to_dict()
    candidates = keys or (
        "security_issues",
        "security_issue",
        "Finding",
        "finding",
        "issue",
        "description",
        "Issue",
    )
    for k in candidates:
        val = data.get(k)
        if val is None or (isinstance(val, float) and pd.isna(val)):
            continue
        if isinstance(val, (list, tuple)):
            val = "; ".join(str(x) for x in val if x)
        text = str(val).strip()
        if text and text.lower() not in {"none", "nan", "[]"}:
            return text
    return default
