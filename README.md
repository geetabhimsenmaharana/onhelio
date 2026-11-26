<div align="center">

# ☀️ onHelio

### Solar answers. Instantly. Every one with its source.

An AI assistant that explains solar equipment, alerts and warranties in plain English, straight from official manufacturer documents.

</div>

---

## What is onHelio?

Solar systems send alerts like *"Module voltage mismatch"* or *"DC isolation disruption"*. The answers are buried in long PDF manuals, and most people who manage solar sites don't have time to read them.

**onHelio reads those documents for you.** Ask a question in your own words and get a short, clear answer, with the exact document and page it came from.

Today onHelio covers **SolarEdge** inverters and power optimizers. More manufacturers are coming.

---

## Who is it for?

| | Role | What onHelio gives you |
|---|---|---|
| 🌱 | **Solar Explorer** | Simple explanations for anyone curious about solar *(default)* |
| 📊 | **Portfolio Manager** | What an alert means, what to tell the technician, and what "fixed" looks like |
| 🔧 | **Technician** | Likely causes, step-by-step checks, parts to bring, act now or monitor |
| 🏠 | **Homeowner** | Plain words and safe checks only |

Pick your role on the left side of the screen, and every answer adapts to you.

---

## What an answer looks like

> **You ask** *(as a Portfolio Manager)*:
> I got a Module voltage mismatch alert. What should I do?

> 🟡 **Schedule a visit** · Confidence: High
>
> One of your panels is producing a different voltage than the others.
>
> **What to do:**
> 1. Send a technician to check that panel and its optimizer *(the small box behind each panel)*.
> 2. Ask them to look for loose or damaged connectors.
> 3. Confirm the alert clears in the monitoring portal after the fix.
>
> 📄 *Source: SolarEdge Troubleshooting Alerts guide, page X*

*Example for illustration. Real answers depend on the documents loaded.*

---

## Features

- 💬 **Ask in plain English.** No need to know the exact alert code or manual name.
- 👤 **Answers for your role.** The same question gets a different answer for a manager than for a technician.
- 🚦 **Severity badge.** 🟢 Monitor · 🟡 Schedule a visit · 🔴 Act now
- 🎯 **Confidence level.** High, Medium or Low, depending on how directly the documents answer your question.
- 📄 **Every answer cites its source.** File name and page, so you can check it yourself.
- 🛑 **No guessing.** If the documents don't cover something, onHelio says so.
- 🧒 **Easy to read.** Short sentences, simple words and numbered steps.

---

## How to use it

1. Open onHelio.
2. Choose your role on the left, or keep **Solar Explorer**.
3. Type your question, for example:
   - *What is a power optimizer?*
   - *How long is the SolarEdge optimizer warranty, and how do I claim it?*
   - *The same DC isolation alert keeps coming back. What should I do?*
4. Read the answer, check the badge, and open **Pages searched** to see the sources.

> ⚠️ onHelio is an information tool, **not a replacement for a qualified solar technician**. Any electrical work must be done by a qualified professional.

---
---

# 🛠️ For developers

Everything you need to run onHelio on your own computer, add documents, or deploy it online.

## How it works

```
PDFs  →  extract text  →  search database  →  Claude writes the answer  →  chat screen
        (pypdf)          (ChromaDB)          (Anthropic API)            (Streamlit)
```

1. **Extract:** every PDF listed in `config.xlsx` is read page by page.
2. **Index:** the text is stored in a local ChromaDB search database.
3. **Search:** for each question, onHelio combines meaning-based search with exact keyword matching, so alert names and error codes are found reliably.
4. **Answer:** Claude answers **only** from the matching pages, in the style of the selected role, and cites the file and page.

**Tech stack:** Python 3.12 · Claude API · ChromaDB · Streamlit · pypdf · pandas

---

## Run it on your computer

**You need:** Python 3.12 and an [Anthropic API key](https://console.anthropic.com).

<details>
<summary><b>Step-by-step setup (about 5 minutes)</b></summary>

<br>

**1. Download the project**
```bash
git clone https://github.com/geetabhimsenmaharana/onhelio.git
cd onhelio
```

**2. Create an environment and install the packages**

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

**3. Add your API key**
```bash
cp .env.example .env
```
Open `.env` and replace `your-key-here` with your own key. `.env` is listed in `.gitignore`, so it is never uploaded.

**4. Start onHelio**
```bash
streamlit run app/streamlit_app.py
```
Your browser opens at `http://localhost:8501`. On the first start, onHelio reads the PDFs and builds its search database automatically (about a minute).

</details>

---

## Add documents or manufacturers

All document settings live in **`config.xlsx`**. No code changes needed.

| Tab | What it holds |
|---|---|
| `config` | Each manufacturer and its PDF folder, e.g. `SolarEdge` → `data/manufacturer/solaredge` |
| `manufacturer_links` | Official links (warranty, support, guides), key info and a "last checked" date |

<details>
<summary><b>Add new PDFs</b></summary>

<br>

Put the PDFs in the manufacturer's folder, then rebuild:
```bash
python app/extract_text.py
python app/build_index.py
```
</details>

<details>
<summary><b>Add a new manufacturer (e.g. Enphase)</b></summary>

<br>

1. Create the folder `data/manufacturer/enphase/` and put its PDFs there.
2. Add a row to the `config` tab of `config.xlsx`: `Enphase` → `data/manufacturer/enphase`.
3. Rebuild with the two commands above.
</details>

---

## Project structure

<details>
<summary><b>See the files</b></summary>

<br>

```
onhelio/
├── app/
│   ├── streamlit_app.py   # chat screen
│   ├── ask.py             # search + Claude answer (also works from the Terminal)
│   ├── extract_text.py    # PDF → text, page by page
│   ├── build_index.py     # text → ChromaDB search database
│   └── check_setup.py     # checks config.xlsx and lists the PDFs found
├── data/manufacturer/     # one folder of PDFs per manufacturer
├── config.xlsx            # manufacturers, folders and official links
├── requirements.txt       # Python packages
├── .env.example           # template for your API key
└── .gitignore             # keeps .env and generated files out of Git
```
</details>

---

## Deploy online

<details>
<summary><b>Streamlit Community Cloud (free)</b></summary>

<br>

1. Push the repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app** → choose the repo → main file `app/streamlit_app.py`.
3. Under **Advanced settings**, choose **Python 3.12** and add this to **Secrets**:
   ```toml
   ANTHROPIC_API_KEY = "your-key-here"
   ```
4. Deploy. The first load builds the search database automatically.

</details>

---

## FAQ

<details>
<summary><b>Is my API key safe?</b></summary>

<br>

Yes. Locally it lives only in `.env`, which `.gitignore` keeps out of Git. Online it lives in Streamlit Secrets, which only the app owner can see. Visitors can use the app but can never read the key.
</details>

<details>
<summary><b>How much does it cost to run?</b></summary>

<br>

Each question costs a fraction of a cent in Anthropic API usage. The app limits each visit to 20 questions and 500 characters per question; change the limit with `MAX_QUESTIONS_PER_SESSION` in `.env` or Streamlit Secrets. Setting a monthly spend limit in the Anthropic Console is recommended.
</details>

<details>
<summary><b>Why Python 3.12 and not the newest version?</b></summary>

<br>

ChromaDB does not install correctly on Python 3.14 yet; pip falls back to an old, incompatible version. Python 3.12 works reliably.
</details>

<details>
<summary><b>Does onHelio make things up?</b></summary>

<br>

It is instructed to answer only from the loaded documents and to say so when they don't cover a question. Every answer lists the pages it used, so you can verify it. Severity and confidence are suggestions; always confirm with a qualified technician.
</details>

<details>
<summary><b>Can I use a different Claude model?</b></summary>

<br>

Yes. Set `CLAUDE_MODEL` in `.env` (default: `claude-sonnet-5-5`).
</details>

<details>
<summary><b>Where do the documents come from?</b></summary>

<br>

The PDFs in `data/manufacturer/` are public documents from the manufacturers' official websites. They belong to their respective owners and are included for reference only. Always check the manufacturer's website for the latest version. Official links are listed in `config.xlsx`.
</details>

---

## Roadmap

- [ ] More manufacturers: Enphase, SMA, Tesla
- [ ] Alert history: *"this alert has happened 3 times this year"*
- [ ] Warranty coverage check: *"who pays for this repair?"*
- [ ] Answer quality tests with RAGAS

---

<div align="center">

Built by **Geeta Bhimsen Maharana**

[LinkedIn](https://www.linkedin.com/in/geetabhimsenmaharana/) · [GitHub](https://github.com/geetabhimsenmaharana)

</div>
