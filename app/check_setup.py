"""Step 4: read config.xlsx and list the PDFs found for each manufacturer."""
from pathlib import Path

import pandas as pd

# The onHelio folder, wherever it lives on this computer (no usernames needed)
ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config.xlsx"


def main():
    config = pd.read_excel(CONFIG, sheet_name="config")
    links = pd.read_excel(CONFIG, sheet_name="manufacturer_links")

    for _, row in config.iterrows():
        name = row["manufacturer"]
        folder = ROOT / row["folder"]
        print(f"\n=== {name} ===")
        print(f"Folder: {folder}")

        if not folder.exists():
            print("  Folder not found. Check the 'folder' column in config.xlsx.")
            continue

        pdfs = sorted(folder.glob("*.pdf"))
        print(f"PDFs found: {len(pdfs)}")
        for pdf in pdfs:
            print(f"  - {pdf.name}")

        n_links = (links["manufacturer"] == name).sum()
        print(f"Links in config: {n_links}")


if __name__ == "__main__":
    main()
