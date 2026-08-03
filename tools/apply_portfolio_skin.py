#!/usr/bin/env python3
"""One-shot: apply portfolio_skin across Streamlit GRC apps."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SKIP = {
    "portfolio_skin.py",
    "fair_risk_calculator.py",  # already migrated
    "ibm_i_audit_core.py",
    "ibm_i_audit_core_fixed.py",
    "jde_audit_core.py",
    "unix_linux_audit_core.py",
    "apply_portfolio_skin.py",
    "make_multipage.py",
}

KICKERS = (
    ("fair", "Quantitative risk"),
    ("roi", "Business case"),
    ("vendor", "Third-party risk"),
    ("third_party", "Third-party risk"),
    ("third party", "Third-party risk"),
    ("compliance", "Compliance"),
    ("csf", "NIST CSF"),
    ("control", "Controls"),
    ("exception", "Controls"),
    ("monte", "Risk management"),
    ("treatment", "Risk management"),
    ("enterprise", "Risk management"),
    ("risk", "Risk management"),
    ("kpi", "Analytics"),
    ("analytics", "Analytics"),
    ("metrics", "Analytics"),
    ("policy", "Governance"),
    ("audit", "Audit"),
    ("calendar", "Compliance"),
    ("asset", "Asset management"),
    ("privacy", "Privacy"),
    ("incident", "Incident response"),
    ("business_continuity", "Resilience"),
    ("business continuity", "Resilience"),
    ("awareness", "Awareness"),
    ("campaign", "Awareness"),
    ("ibm", "IBM i"),
    ("jde", "JD Edwards"),
    ("unix", "Unix / Linux"),
    ("home", "Toolkit"),
)


def kicker_for(name: str) -> str:
    stem = name.lower().replace("-", " ").replace("_", " ")
    for key, label in KICKERS:
        if key in stem:
            return label
    return "GRC tooling"


def strip_css_block(text: str) -> str:
    patterns = [
        r'(?ms)^# Custom CSS.*?\nst\.markdown\(\s*""".*?"""\s*,\s*unsafe_allow_html\s*=\s*True\s*\)\s*\n?',
        r'(?ms)^st\.markdown\(\s*"""\s*\n<style>.*?"""\s*,\s*unsafe_allow_html\s*=\s*True\s*\)\s*\n?',
        r"(?ms)^st\.markdown\(\s*'''\s*\n<style>.*?'''\s*,\s*unsafe_allow_html\s*=\s*True\s*\)\s*\n?",
        r'(?ms)st\.markdown\(\s*"""\s*\n<style>.*?</style>\s*"""\s*,\s*unsafe_allow_html\s*=\s*True\s*\)\s*\n?',
    ]
    out = text
    for pat in patterns:
        out2, n = re.subn(pat, "\n", out, count=1)
        if n:
            return out2
    return out


def ensure_import(text: str) -> str:
    if re.search(r"^import portfolio_skin\b", text, re.M):
        return text
    m = re.search(r"^(import streamlit as st.*\n)", text, re.M)
    if m:
        return text[: m.end()] + "import portfolio_skin\n" + text[m.end() :]
    return "import portfolio_skin\n" + text


def patch_page_config(text: str, *, uses_sidebar: bool) -> str:
    sidebar_state = "expanded" if uses_sidebar else "collapsed"
    hide = not uses_sidebar

    def repl(match: re.Match) -> str:
        block = match.group(0)
        title_m = re.search(r'page_title\s*=\s*["\']([^"\']+)["\']', block)
        title = title_m.group(1) if title_m else "GRC Tool"
        title = title.replace(" · i on GRC", "")
        lines = [
            "st.set_page_config(",
            f'    page_title="{title} · i on GRC",',
            '    page_icon="assets/favicon.svg",',
            '    layout="wide",',
            f'    initial_sidebar_state="{sidebar_state}",',
            ")",
            "",
            f"portfolio_skin.apply(hide_sidebar={hide})",
            "",
        ]
        return "\n".join(lines)

    text = re.sub(r"\nportfolio_skin\.apply\([^\n]*\)\n?", "\n", text)
    new, n = re.subn(
        r"st\.set_page_config\([^)]*\)",
        repl,
        text,
        count=1,
        flags=re.S,
    )
    return new if n else text


def replace_header(text: str, *, kicker: str) -> str:
    pat = re.compile(
        r"[ \t]*st\.markdown\(\s*(?P<q>['\"])"
        r"<h1 class=(?P<q2>['\"])main-header(?P=q2)>(?P<title>.*?)</h1>"
        r"(?P=q)\s*,\s*unsafe_allow_html\s*=\s*True\s*\)\n?"
        r"(?:[ \t]*st\.write\(\s*(?P<q3>['\"])(?P<lede>.*?)(?P=q3)\s*\)\n?)?",
        re.S,
    )

    def repl(match: re.Match) -> str:
        title = re.sub(r"\s+", " ", match.group("title")).strip().replace('"', '\\"')
        lede = (match.group("lede") or "").strip().replace('"', '\\"')
        if not lede:
            lede = "Interactive GRC tool — #RUNGRCRaleigh build-in-public."
        indent = re.match(r"[ \t]*", match.group(0)).group(0)
        return (
            f"{indent}portfolio_skin.page_header(\n"
            f'{indent}    title="{title}",\n'
            f'{indent}    lede="{lede}",\n'
            f'{indent}    kicker="{kicker}",\n'
            f"{indent})\n"
        )

    new, n = pat.subn(repl, text, count=1)
    return new if n else text


def migrate_file(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if "streamlit" not in text:
        return "skip-not-streamlit"

    uses_sidebar = bool(re.search(r"\bst\.sidebar\b|\bwith st\.sidebar\b", text))
    kicker = kicker_for(path.stem)
    text = strip_css_block(text)
    text = ensure_import(text)
    text = patch_page_config(text, uses_sidebar=uses_sidebar)
    text = replace_header(text, kicker=kicker)
    path.write_text(text, encoding="utf-8", newline="\n")
    return f"ok sidebar={uses_sidebar}"


def main() -> None:
    targets: list[Path] = []
    for p in sorted(ROOT.glob("*.py")):
        if p.name not in SKIP:
            targets.append(p)
    pages = ROOT / "pages"
    if pages.is_dir():
        targets.extend(sorted(pages.glob("*.py")))

    results = []
    for p in targets:
        try:
            status = migrate_file(p)
        except Exception as exc:  # noqa: BLE001
            status = f"ERR {exc}"
        results.append((str(p.relative_to(ROOT)), status))

    home = ROOT / "Home.py"
    home.write_text(
        "\n".join(
            [
                "import streamlit as st",
                "import portfolio_skin",
                "",
                "st.set_page_config(",
                '    page_title="GRC Streamlit Hub · i on GRC",',
                '    page_icon="assets/favicon.svg",',
                '    layout="wide",',
                '    initial_sidebar_state="expanded",',
                ")",
                "",
                "portfolio_skin.apply(hide_sidebar=False)",
                "portfolio_skin.page_header(",
                '    title="GRC Streamlit Hub",',
                '    lede="Pick a tool from the sidebar. Club builds under #RUNGRCRaleigh.",',
                '    kicker="Toolkit",',
                ")",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    results.append(("Home.py", "ok-rewritten"))

    for path, status in results:
        print(f"{status:28} {path}")


if __name__ == "__main__":
    main()
