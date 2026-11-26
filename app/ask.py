"""Step 7: ask onHelio a question from the Terminal.

ChromaDB finds the most relevant PDF pieces; Claude writes the answer with sources.
Usage:  python app/ask.py "How long is the SolarEdge optimizer warranty?"
"""
import os
import sys
from pathlib import Path

import anthropic
import chromadb
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

DB_PATH = ROOT / "db" / "chroma"
COLLECTION = "onhelio_docs"
MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")
TOP_K = 4

SYSTEM_PROMPT = """You are onHelio, a solar O&M assistant for asset managers, technicians and homeowners.
Rules:
- Answer ONLY from the provided document excerpts. If they don't contain the answer, say so plainly.
- Cite every fact as (file name, page X).
- For any electrical work, say it must be done by a qualified technician.

How to write:
- Write so a 5th grader can understand: short sentences, everyday words.
- If you must use a technical word, explain it in brackets, e.g. "inverter (the box that turns solar power into home power)".
- Start with a one-sentence direct answer.
- Use numbered steps (1, 2, 3) for anything the reader should do in order. Use short bullets for everything else.
- No long paragraphs. Keep the whole answer short.

Header (required):
The first two lines of your reply must be exactly:
SEVERITY: green | yellow | red | none
CONFIDENCE: high | medium | low
- Severity: green = monitor, yellow = schedule a visit, red = act now, none = not about a fault.
- Confidence: high = the excerpts state the answer directly; medium = the excerpts only partly cover it;
  low = the excerpts barely cover it.
Do not mention severity or confidence anywhere else in the answer."""

SEVERITIES = ("green", "yellow", "red", "none")
CONFIDENCES = ("high", "medium", "low")


def split_header(text):
    """Pull the SEVERITY and CONFIDENCE lines off the top of the reply.

    Returns (severity, confidence, answer). Missing or odd values fall back to 'none' / ''.
    """
    severity, confidence, body = "none", "", []
    for line in text.strip().splitlines():
        key, _, value = line.partition(":")
        key, value = key.strip().upper(), value.strip().lower()
        if not body and key == "SEVERITY":
            severity = value if value in SEVERITIES else "none"
        elif not body and key == "CONFIDENCE":
            confidence = value if value in CONFIDENCES else ""
        else:
            body.append(line)
    return severity, confidence, "\n".join(body).strip()

# How the answer should be shaped for each type of user
DEFAULT_ROLE = "Solar Explorer"

ROLE_GUIDE = {
    "Solar Explorer": (
        "The user is curious and wants to learn about solar. They may have no background at all. "
        "Explain the idea simply, like a friendly teacher, with a short real-life example if it helps. "
        "Never suggest touching or opening equipment."
    ),
    "Portfolio Manager": (
        "The user manages solar sites and coordinates work but is not a technician. "
        "Give: what it means in one plain sentence, what to ask or tell the technician, "
        "and what 'fixed' looks like. Avoid deep technical detail."
    ),
    "Technician": (
        "The user is a qualified solar technician. "
        "Give: likely causes, step-by-step checks and fixes, parts that may be needed, "
        "and whether to act now or monitor. Be precise and practical."
    ),
    "Homeowner": (
        "The user is a homeowner with no technical background. "
        "Use very simple words. Only suggest safe checks (looking at lights, the app, the breaker label). "
        "Never suggest opening equipment. Tell them when to call their installer."
    ),
}


STOPWORDS = set("""a an and are as at be but by can do does for from got has have how i if in is it its
me my of on or our should so that the their them then there this to was we what when where which who why
will with you your""".split())


def keyword_score(question, text):
    """Score a chunk by exact word and phrase matches (good for alert names and error codes)."""
    words = [w for w in "".join(c if c.isalnum() else " " for c in question.lower()).split()
             if w not in STOPWORDS and len(w) > 2]
    text = " ".join(text.lower().split())
    score = sum(1 for w in set(words) if w in text)
    # Bonus for two- and three-word phrases, e.g. "voltage mismatch", "module voltage mismatch"
    for n in (2, 3):
        for i in range(len(words) - n + 1):
            if " ".join(words[i:i + n]) in text:
                score += 3 * n
    return score


def search(question):
    """Hybrid search: meaning-based (ChromaDB) + exact keyword matches, merged without duplicates."""
    client = chromadb.PersistentClient(path=str(DB_PATH))
    collection = client.get_collection(COLLECTION)

    # 1) Meaning-based search
    result = collection.query(query_texts=[question], n_results=TOP_K)
    hits = list(zip(result["ids"][0], result["documents"][0], result["metadatas"][0]))

    # 2) Keyword search over all chunks (fast: the knowledge base is small)
    everything = collection.get(include=["documents", "metadatas"])
    scored = sorted(
        zip(everything["ids"], everything["documents"], everything["metadatas"]),
        key=lambda item: keyword_score(question, item[1]),
        reverse=True,
    )
    keyword_hits = [item for item in scored[:TOP_K] if keyword_score(question, item[1]) >= 6]

    # 3) Keyword hits first (exact matches are most reliable), then meaning-based, no duplicates
    merged, seen = [], set()
    for chunk_id, doc, meta in keyword_hits + hits:
        if chunk_id not in seen:
            seen.add(chunk_id)
            merged.append((doc, meta))
    return merged[:TOP_K * 2]


def ask(question, role=DEFAULT_ROLE):
    excerpts = search(question)
    system = f"{SYSTEM_PROMPT}\n\n{ROLE_GUIDE.get(role, ROLE_GUIDE[DEFAULT_ROLE])}"
    context = "\n\n".join(
        f"[{meta['source_file']}, page {meta['page']}]\n{doc}" for doc, meta in excerpts
    )
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from .env
    response = client.messages.create(
        model=MODEL,
        max_tokens=800,
        system=system,
        messages=[{
            "role": "user",
            "content": f"Document excerpts:\n\n{context}\n\nQuestion: {question}",
        }],
    )
    # The reply can contain several blocks (e.g. a "thinking" block first); keep only the text ones
    answer = "\n".join(block.text for block in response.content if block.type == "text").strip()
    return answer or "SEVERITY: none\nCONFIDENCE: low\nSorry, I couldn't produce an answer. Please try again.", excerpts


def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        sys.exit("Missing ANTHROPIC_API_KEY. Add it to the .env file in the onhelio folder.")

    question = " ".join(sys.argv[1:]) or "How many years is the power optimizer warranty?"
    answer, excerpts = ask(question)

    severity, confidence, answer = split_header(answer)
    print(f"\nQuestion: {question}\nSeverity: {severity} | Confidence: {confidence or 'n/a'}\n")
    print(answer)
    print("\nSearched:")
    for _, meta in excerpts:
        print(f"  - {meta['source_file']} (page {meta['page']})")


if __name__ == "__main__":
    main()
