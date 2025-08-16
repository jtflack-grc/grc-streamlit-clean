# tools/make_multipage.py
from pathlib import Path
import shutil, re

root = Path(".")
pages = root / "pages"
pages.mkdir(exist_ok=True)

SKIP = {"Home.py", "__init__.py", "setup.py", "requirements.py"}  # add more if needed

apps = sorted([p for p in root.glob("*.py") if p.name not in SKIP])
for i, src in enumerate(apps, start=1):
    title = re.sub(r"[_-]+", " ", src.stem).title()
    dst = pages / f"{i:02d} - {title}.py"
    shutil.copy2(src, dst)

home = root / "Home.py"
if not home.exists():
    home.write_text(
        "import streamlit as st\n"
        "st.set_page_config(page_title='GRC Streamlit – Hub', layout='wide')\n"
        "st.title('GRC Streamlit – App Hub')\n"
        "st.write('Use the sidebar to open any app. Each page is a copy of your original .py file.')\n",
        encoding="utf-8",
    )

print(f"Created {len(apps)} pages under /pages and a Home.py (if missing).")
print('Run locally with:  streamlit run Home.py')
