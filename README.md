# ☀️ onHelio

**Solar answers. Instantly. Every one with its source.**

onHelio is an AI assistant for solar operations and maintenance (O&M). Ask a question in plain English — about an inverter alert, a warranty, or how solar works — and onHelio answers from official manufacturer documents, in simple language, with the file and page it came from.

It currently covers **SolarEdge** inverters and power optimizers. Other manufacturers can be added without changing any code.

---

## Why onHelio?

People who manage solar sites are expected to understand every alert, warranty and fault — but the answers are buried in long PDFs. onHelio reads those documents for you and answers differently depending on who is asking:

| Role | What you get |
|---|---|
| **Solar Explorer** *(default)* | Simple explanations for anyone curious about solar |
| **Portfolio Manager** | What an alert means, what to tell the technician, what "fixed" looks like |
| **Technician** | Likely causes, step-by-step checks, parts, act now or monitor |
| **Homeowner** | Plain words and safe checks only |

Every answer shows:
- a **severity badge** — 🟢 Monitor · 🟡 Schedule a visit · 🔴 Act now (for fault questions)
- a **confidence level** — High / Medium / Low, based on how directly the documents answer it
- the **sources** — file name and page

---

## How it works

```
PDFs ──► text extraction ──► search database (ChromaDB) ──► Claude writes the answer ──► chat screen (Streamlit)
```

1. `extract_text.py` reads every PDF listed in `config.xlsx`, page by page.
2. `build_index.py` stores the text in a local ChromaDB search database.
3. `ask.py` finds the most relevant pages (meaning-based + exact keyword search) and asks Claude to answer **only** from them.
4. `streamlit_app.py` is the chat screen.

**Tech stack:** Python 3.12 · Claude API (Anthropic) · ChromaDB · Streamlit · pypdf · pandas

---

## Quick start (about 5 minutes)

### 1. Requirements
- **Python 3.12** (ChromaDB does not install correctly on Python 3.14 yet)
- An **Anthropic API key** — create one at [console.anthropic.com](https://console.anthropic.com)

### 2. Download the project
```bash
git clone https://github.com/<your-username>/onhelio.git
cd onhelio
```

### 3. Create an environment and install
With Anaconda:
```bash
conda create -n onhelio python=3.12 -y
conda activate onhelio
pip install -r requirements.txt
```
Or with plain Python 3.12:
```bash
python3.12 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Add your API key
Copy the example file and paste your key into it:
```bash
cp .env.example .env
```
Then open `.env` and replace `your-key-here` with your key. **`.env` is never uploaded to GitHub** (it is listed in `.gitignore`).

### 5. Run
```bash
streamlit run app/streamlit_app.py
```
Your browser opens at `http://localhost:8501`. On the first start onHelio reads the PDFs and builds its search database automatically (about a minute).

---

## Using onHelio

1. Pick your role on the left (or keep **Solar Explorer**).
2. Ask a question, for example:
   - *What is a power optimizer?*
   - *I got a Module voltage mismatch alert. What should I do?*
   - *How long is the SolarEdge optimizer warranty, and how do I claim it?*
3. Check the badge, the confidence level and the **Pages searched** list.

If the documents don't contain the answer, onHelio says so instead of guessing.

You can also ask from the Terminal:
```bash
python app/ask.py "How long is the SolarEdge optimizer warranty?"
```

---

## Adding or updating documents

All document settings live in **`config.xlsx`** — no code changes needed.

| Tab | What it holds |
|---|---|
| `config` | One row per manufacturer and the folder its PDFs are in, e.g. `SolarEdge` → `data/manufacturer/solaredge` |
| `manufacturer_links` | Official links (warranty, support, guides) with key info and a "last checked" date |

**To add PDFs:** put them in the manufacturer's folder, then rebuild:
```bash
python app/extract_text.py
python app/build_index.py
```

**To add a new manufacturer (e.g. Enphase):**
1. Create `data/manufacturer/enphase/` and put its PDFs there.
2. Add a row to the `config` tab: `Enphase` → `data/manufacturer/enphase`.
3. Run the two rebuild commands above.

---

## Project structure

```
onhelio/
├── app/
│   ├── streamlit_app.py   # chat screen
│   ├── ask.py             # search + Claude answer (also works from the Terminal)
│   ├── extract_text.py    # PDF → text, page by page
│   ├── build_index.py     # text → ChromaDB search database
│   └── check_setup.py     # checks config.xlsx and lists the PDFs found
├── data/manufacturer/     # one folder of PDFs per manufacturer
├── .streamlit/config.toml # colors and theme
├── config.xlsx            # manufacturers, folders and official links
├── requirements.txt       # Python packages
└── .env.example           # template for your API key
```

---

## Deploying online (Streamlit Community Cloud)

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io), choose **New app**, pick the repo, and set the main file to `app/streamlit_app.py`.
3. In **Advanced settings**, choose **Python 3.12**, and under **Secrets** add:
   ```toml
   ANTHROPIC_API_KEY = "your-key-here"
   ```
4. Deploy. The first load builds the search database automatically.

**Cost protection:** the app limits each visit to 20 questions and 500 characters per question. You can change the limit with `MAX_QUESTIONS_PER_SESSION` in `.env` or Streamlit secrets. Also set a **monthly spend limit** in the Anthropic Console.

---

## Safety and disclaimer

- onHelio is an information tool, **not a substitute for a qualified solar technician**. Any electrical work must be done by a qualified professional.
- Severity and confidence are onHelio's suggestions. Always confirm with the manufacturer's documents and your technician.
- Manufacturer documents in `data/manufacturer/` belong to their respective owners and are included for reference only. Always check the manufacturer's website for the latest version.

---

## Roadmap

- More manufacturers (Enphase, SMA, Tesla)
- Alert history: "this alert has happened 3 times this year"
- Warranty coverage check: "who pays for this repair?"
- Evaluation with RAGAS and automated tests

---

Built by **Geeta Bhimsen Maharana** · [LinkedIn](https://www.linkedin.com/in/geetabhimsenmaharana/) · [GitHub](https://github.com/geetabhimsenmaharana)
