"""Step 5: pull the text out of every PDF, page by page.

Output: data/processed/<manufacturer>/<pdf name>.json
Each file holds one entry per page, so answers can cite the page later.
"""
import json
from pathlib import Path

import pandas as pd
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config.xlsx"
OUT_DIR = ROOT / "data" / "processed"


def extract_pdf(pdf_path):
    """Return a list of {page, text} for one PDF."""
    reader = PdfReader(pdf_path)
    pages = []
    for number, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        pages.append({"page": number, "text": text})
    return pages


def main():
    config = pd.read_excel(CONFIG, sheet_name="config")

    for _, row in config.iterrows():
        name = row["manufacturer"]
        folder = ROOT / row["folder"]
        out_folder = OUT_DIR / name.lower()
        out_folder.mkdir(parents=True, exist_ok=True)
        print(f"\n=== {name} ===")

        for pdf in sorted(folder.glob("*.pdf")):
            pages = extract_pdf(pdf)
            record = {"manufacturer": name, "source_file": pdf.name, "pages": pages}
            out_file = out_folder / f"{pdf.stem}.json"
            out_file.write_text(json.dumps(record, indent=2, ensure_ascii=False))

            words = sum(len(p["text"].split()) for p in pages)
            empty = sum(1 for p in pages if not p["text"])
            note = f"  ({empty} pages had no text - may be scanned images)" if empty else ""
            print(f"  {pdf.name}: {len(pages)} pages, {words} words{note}")

    print(f"\nSaved to: {OUT_DIR}")


if __name__ == "__main__":
    main()
