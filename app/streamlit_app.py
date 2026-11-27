"""Step 8: onHelio chat screen.

Run:  streamlit run app/streamlit_app.py
Uses the same search + Claude logic as ask.py.
"""
import os
from datetime import datetime

import streamlit as st

from ask import DB_PATH, DEFAULT_ROLE, ROLE_GUIDE, ask, split_header

# Cost protection for the public app (change in .env / Streamlit secrets if needed)
MAX_QUESTIONS = int(os.getenv("MAX_QUESTIONS_PER_SESSION", "20"))
MAX_QUESTION_CHARS = 500


def greeting():
     
    return "onHelio"

# Badge look and meaning for each severity level
BADGES = {
    "green":  ("Monitor",          "#E8F5E9", "#1B5E20"),
    "yellow": ("Schedule a visit", "#FFF8E1", "#8A5A00"),
    "red":    ("Act now",          "#FDECEA", "#B71C1C"),
}


def badge_html(level):
    """Small rounded pill shown above an answer. Nothing is shown for 'none'."""
    if level not in BADGES:
        return ""
    label, bg, fg = BADGES[level]
    return (f'<span style="background:{bg};color:{fg};padding:4px 12px;border-radius:999px;'
            f'font-size:0.85rem;font-weight:600;">● {label}</span>')


def confidence_html(level):
    """Quiet grey label, e.g. 'Confidence: High'."""
    if not level:
        return ""
    return (f'<span style="color:#6e6e73;font-size:0.85rem;margin-left:10px;">'
            f'Confidence: {level.capitalize()}</span>')


def header_html(severity, confidence):
    """Severity badge and confidence label on one line, above the answer."""
    return badge_html(severity) + confidence_html(confidence)

st.set_page_config(page_title="onHelio", page_icon="☀️", layout="centered",
                   initial_sidebar_state="expanded")

# Clean, calm look: system font, more white space, hide Streamlit's default menu and footer
st.markdown("""
<style>
html, body, [class*="css"] { font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", sans-serif; }
footer { visibility: hidden; }
.block-container { padding-top: 4rem; max-width: 720px; }
.oh-logo { font-size: 1.6rem; font-weight: 600; letter-spacing: -0.02em; margin: 0 0 1.5rem 0; }
.oh-greeting { font-size: 2.2rem; font-weight: 500; letter-spacing: -0.02em; text-align: center; margin-top: 3rem; }
.oh-sub { font-size: 1.05rem; color: #6e6e73; text-align: center; margin-bottom: 2.5rem; }
.oh-accent { background: linear-gradient(90deg, #F59E0B, #F97316); -webkit-background-clip: text; background-clip: text; color: transparent; }
[data-testid="stChatInput"] textarea:focus { border-color: #F59E0B !important; }
</style>
""", unsafe_allow_html=True)

if not os.getenv("ANTHROPIC_API_KEY"):
    st.error("Missing ANTHROPIC_API_KEY. Add it to the .env file in the onhelio folder.")
    st.stop()


@st.cache_resource(show_spinner="First start: reading the documents and building the search index...")
def ensure_index():
    """Build the search database from the PDFs if it doesn't exist yet (e.g. first run online)."""
    if not (DB_PATH / "chroma.sqlite3").exists():
        import build_index
        import extract_text
        extract_text.main()
        build_index.main()
    return True


ensure_index()

# Sidebar: who is asking? Answers adapt to the role.
with st.sidebar:
    st.markdown('<div class="oh-logo">on<span class="oh-accent">Helio</span></div>', unsafe_allow_html=True)
    st.subheader("I am a...")
    roles = list(ROLE_GUIDE.keys())
    role = st.radio("Role", roles, index=roles.index(DEFAULT_ROLE), label_visibility="collapsed")
    st.caption({
        "Solar Explorer": "Curious about solar? Simple explanations and examples.",
        "Portfolio Manager": "Plain meaning, what to tell the technician, what fixed looks like.",
        "Technician": "Causes, step-by-step fixes, parts, act now or monitor.",
        "Homeowner": "Simple words and safe checks only.",
    }[role])

    st.divider()
    st.subheader("Severity")
    for level in ("green", "yellow", "red"):
        st.markdown(badge_html(level), unsafe_allow_html=True)
        st.caption({
            "green": "No urgent action. Keep an eye on it.",
            "yellow": "Needs a technician visit soon.",
            "red": "Safety or major production risk. Act today.",
        }[level])
    st.caption("Severity is onHelio's suggestion. Always confirm with a qualified technician.")

    st.divider()
    st.subheader("Confidence")
    st.caption("**High:** the documents say it directly.  \n"
               "**Medium:** the documents only partly cover it.  \n"
               "**Low:** the documents barely cover it. Double-check.")

# Keep the conversation on screen while the app is open
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        header = header_html(message.get("severity"), message.get("confidence"))
        if header:
            st.markdown(header, unsafe_allow_html=True)
        st.markdown(message["content"])

# Empty chat: centered greeting and tagline, like Claude's start screen
if not st.session_state.messages:
    st.markdown(f'<div class="oh-greeting">☀️ {greeting()}</div>', unsafe_allow_html=True)
    st.markdown('<div class="oh-sub">Select your role on the left, then ask your question.</div>',
                unsafe_allow_html=True)

asked = sum(1 for m in st.session_state.messages if m["role"] == "user")
if asked >= MAX_QUESTIONS:
    st.info(f"You've reached the limit of {MAX_QUESTIONS} questions for this visit. "
            "Refresh the page later to start again.")
    st.stop()

question = st.chat_input("Ask anything about your solar system", max_chars=MAX_QUESTION_CHARS)
if question:
    # Conversation memory: earlier messages go to Claude so follow-up questions make sense.
    # Answers get their SEVERITY/CONFIDENCE header back so Claude keeps the same reply format.
    history = []
    for m in st.session_state.messages:
        if m["role"] == "assistant":
            content = (f"SEVERITY: {m.get('severity') or 'none'}\n"
                       f"CONFIDENCE: {m.get('confidence') or 'medium'}\n{m['content']}")
        else:
            content = m["content"]
        history.append({"role": m["role"], "content": content})

    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching documents..."):
            raw_answer, excerpts = ask(question, role, history)
        severity, confidence, answer = split_header(raw_answer)
        st.caption(f"Answering for: {role}")
        header = header_html(severity, confidence)
        if header:
            st.markdown(header, unsafe_allow_html=True)
        st.markdown(answer)
        with st.expander("Pages searched"):
            for _, meta in excerpts:
                st.write(f"- {meta['source_file']} (page {meta['page']})")

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "severity": severity, "confidence": confidence}
    )
