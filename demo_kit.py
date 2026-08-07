"""Shared interaction helpers for Streamlit club demos (mechanics only)."""

from __future__ import annotations

from typing import Optional

import pandas as pd
import streamlit as st

_SEED_KEY = "demo_kit_seed"


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
