import streamlit as st
from google import genai
import os
import json
import time
import base64
import html
import streamlit.components.v1 as components

# =========================================================
# FALLACY FINDER — HACK TITANS
# Clean cinematic Streamlit version
# =========================================================

st.set_page_config(
    page_title="Fallacy Finder | Hack Titans",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------- AI ----------------

# Streamlit Cloud secrets first, environment variable second.
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    API_KEY = os.environ.get("GEMINI_API_KEY", "")

API_KEY = API_KEY.strip() if isinstance(API_KEY, str) else API_KEY

if not API_KEY:
    st.error("🔑 GEMINI_API_KEY is missing. Add it in Streamlit Cloud → Settings → Secrets.")
    st.stop()


client = genai.Client(api_key=API_KEY)

# Optional diagnostic: confirms the API key + model before a debate.
with st.expander("🔧 Gemini connection test"):
    if st.button("Test Gemini API", key="test_gemini_api"):
        try:
            test_response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents="Reply with exactly: GEMINI_OK",
            )
            st.success(f"Gemini connected: {test_response.text.strip()}")
        except Exception as exc:
            st.error("Gemini connection failed.")
            st.code(str(exc), language="text")


def judge_arguments(topic, argument_a, argument_b):
    prompt = f"""
You are an impartial debate judge and logical fallacy expert.

The topic and arguments may be written in Tanglish (Tamil written using English/Roman letters,
often mixed with English). Understand Tanglish naturally.

Topic:
{topic}

Argument A:
{argument_a}

Argument B:
{argument_b}

Judge ONLY the reasoning and evidence in the text itself.

Score each argument from 0-10 for:
- logic
- evidence
- persuasiveness

Also identify logical fallacies in each argument.
If there are none, return [].

Write "reason" and "overall_reason" in simple Tanglish.
Keep fallacy names in English.

Return ONLY valid JSON in this exact structure:

{{
  "argument_a": {{
    "logic": 0,
    "evidence": 0,
    "persuasiveness": 0,
    "reason": "text",
    "fallacies": []
  }},
  "argument_b": {{
    "logic": 0,
    "evidence": 0,
    "persuasiveness": 0,
    "reason": "text",
    "fallacies": []
  }},
  "winner": "A or B",
  "overall_reason": "text"
}}
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )

    raw = (response.text or "").strip()

    # Safely remove optional Markdown JSON fences.
    if raw.startswith("```"):
        lines = raw.splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        raw = "\n".join(lines).strip()

    if not raw:
        raise ValueError("Gemini returned an empty response.")

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "Gemini returned text that was not valid JSON. "
            f"Response preview: {raw[:300]}"
        ) from exc


# ---------------- Background image ----------------

@st.cache_data
def get_background():
    try:
        with open("assets/background.jpg", "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return ""


BG = get_background()

if BG:
    background_css = (
        'background-image:linear-gradient(rgba(5,3,14,.62),rgba(5,3,14,.90)),'
        'url("data:image/jpeg;base64,' + BG + '");'
    )
else:
    background_css = (
        'background-image:linear-gradient(rgba(5,3,14,.80),rgba(5,3,14,.96));'
    )


# =========================================================
# GLOBAL CSS
# IMPORTANT: normal string, NOT an f-string
# =========================================================

CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Space+Grotesk:wght@500;600;700&display=swap');

:root {
    --bg: #05030d;
    --panel: rgba(10, 8, 22, 0.78);
    --purple: #a855f7;
    --pink: #f472b6;
    --cyan: #22d3ee;
    --gold: #facc15;
    --green: #4ade80;
    --white: #f8fafc;
    --muted: #8f879a;
}

* {
    box-sizing: border-box;
}

html, body, [class*="css"] {
    font-family: "Inter", sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 15% 10%, rgba(168, 85, 247, .14), transparent 28%),
        radial-gradient(circle at 85% 25%, rgba(34, 211, 238, .09), transparent 25%),
        radial-gradient(circle at 50% 100%, rgba(244, 114, 182, .08), transparent 30%),
        var(--bg);
    color: var(--white);
}

header[data-testid="stHeader"] {
    background: transparent !important;
}

footer,
#MainMenu {
    visibility: hidden;
}

.main .block-container {
    max-width: 1220px;
    padding: 1.4rem 1.3rem 4rem;
}

/* ---------- ambient ---------- */

.bg-layer {
    position: fixed;
    inset: -7%;
    z-index: -10;
    background-size: cover;
    background-position: center;
    background-image:linear-gradient(rgba(5,3,14,.80),rgba(5,3,14,.96));
    filter: saturate(1.08);
    animation: bgFloat 26s ease-in-out infinite alternate;
}

@keyframes bgFloat {
    from { transform: scale(1); }
    to { transform: scale(1.07) translate(-1%, -1%); }
}

.ambient {
    position: fixed;
    inset: 0;
    overflow: hidden;
    pointer-events: none;
    z-index: -9;
}

.ambient span {
    position: absolute;
    border-radius: 50%;
    filter: blur(90px);
    opacity: .17;
    animation: drift 16s ease-in-out infinite alternate;
}

.ambient .one {
    width: 420px;
    height: 420px;
    left: -120px;
    top: 0;
    background: var(--purple);
}

.ambient .two {
    width: 360px;
    height: 360px;
    right: -100px;
    top: 20%;
    background: var(--cyan);
    animation-delay: -6s;
}

.ambient .three {
    width: 340px;
    height: 340px;
    left: 42%;
    bottom: -170px;
    background: var(--pink);
    animation-delay: -10s;
}

@keyframes drift {
    from { transform: translate(0, 0) scale(.92); }
    to { transform: translate(55px, -30px) scale(1.12); }
}

body::before {
    content: "";
    position: fixed;
    inset: 0;
    z-index: 50;
    pointer-events: none;
    opacity: .10;
    background:
        repeating-linear-gradient(
            0deg,
            rgba(255,255,255,.05) 0 1px,
            transparent 1px 5px
        );
}

body::after {
    content: "";
    position: fixed;
    inset: 0;
    z-index: 51;
    pointer-events: none;
    opacity: .11;
    background:
        radial-gradient(circle at 20% 20%, rgba(255,255,255,.25) 0 1px, transparent 2px),
        radial-gradient(circle at 75% 35%, rgba(255,255,255,.20) 0 1px, transparent 2px),
        radial-gradient(circle at 55% 78%, rgba(255,255,255,.18) 0 1px, transparent 2px);
    background-size: 180px 180px, 240px 240px, 310px 310px;
    animation: starsMove 22s linear infinite;
}

@keyframes starsMove {
    from { transform: translate(0, 0); }
    to { transform: translate(-32px, 22px); }
}

/* ---------- main typography ---------- */

.brand {
    width: fit-content;
    margin: 0 auto 1.2rem;
    display: flex;
    align-items: center;
    gap: .6rem;
    padding: .55rem .9rem;
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 999px;
    background: rgba(7,5,16,.62);
    box-shadow:
        0 0 34px rgba(168,85,247,.10),
        inset 0 1px 0 rgba(255,255,255,.04);
}

.brand-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 12px rgba(74,222,128,.85);
    animation: dotPulse 1.5s infinite;
}

@keyframes dotPulse {
    50% { transform: scale(1.25); opacity: .65; }
}

.brand-name {
    font-family: "Space Grotesk", sans-serif;
    font-weight: 900;
    font-size: .76rem;
    letter-spacing: .26em;
    padding-left: .26em;
}

.brand-small {
    color: #655e70;
    font-size: .56rem;
    letter-spacing: .12em;
}

.hero-title {
    text-align: center;
    font-family: "Space Grotesk", sans-serif;
    font-size: clamp(3rem, 6vw, 5.3rem);
    line-height: .9;
    font-weight: 900;
    letter-spacing: -.06em;
    background: linear-gradient(
        110deg,
        #ffffff,
        #ddd6fe,
        #a855f7,
        #f472b6,
        #22d3ee
    );
    background-size: 260% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: titleFlow 7s linear infinite;
}

@keyframes titleFlow {
    to { background-position: 260% 50%; }
}

.hero-sub {
    text-align: center;
    margin: .7rem auto 1.4rem;
    color: #777082;
    font-size: .76rem;
    font-weight: 800;
    letter-spacing: .18em;
    text-transform: uppercase;
}

/* ---------- section ---------- */

.section {
    margin: 1.4rem 0 .75rem;
    color: #c9b8e9;
    font-size: .67rem;
    font-weight: 900;
    letter-spacing: .18em;
    text-transform: uppercase;
}

/* ---------- inputs ---------- */

.stTextInput > div > div,
.stTextArea > div > div {
    background: rgba(255,255,255,.025) !important;
    border: 1px solid rgba(255,255,255,.09) !important;
    border-radius: 15px !important;
}

.stTextInput > div > div:focus-within,
.stTextArea > div > div:focus-within {
    border-color: rgba(168,85,247,.72) !important;
    box-shadow:
        0 0 0 3px rgba(168,85,247,.09),
        0 0 30px rgba(168,85,247,.12) !important;
}

.stTextInput input,
.stTextArea textarea {
    color: #ffffff !important;
    background: transparent !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #5f5968 !important;
}

label[data-testid="stWidgetLabel"] p {
    color: #c4b5fd !important;
    font-size: .74rem !important;
    font-weight: 800 !important;
}

/* ---------- argument tags ---------- */

.arg {
    display: inline-flex;
    align-items: center;
    gap: .4rem;
    padding: .44rem .72rem;
    border-radius: 999px;
    font-size: .67rem;
    font-weight: 900;
    letter-spacing: .08em;
    margin-bottom: .55rem;
}

.arg-a {
    color: #67e8f9;
    background: rgba(34,211,238,.07);
    border: 1px solid rgba(34,211,238,.27);
}

.arg-b {
    color: #e9b8ff;
    background: rgba(168,85,247,.08);
    border: 1px solid rgba(168,85,247,.30);
}

/* ---------- buttons ---------- */

.stButton > button {
    width: 100%;
    min-height: 54px;
    border: 0 !important;
    border-radius: 16px !important;
    color: #ffffff !important;
    font-size: .86rem !important;
    font-weight: 900 !important;
    letter-spacing: .05em;
    background: linear-gradient(
        100deg,
        #6d38d9,
        #a855f7,
        #ec4899,
        #6d38d9
    ) !important;
    background-size: 250% 100% !important;
    box-shadow:
        0 14px 40px rgba(168,85,247,.28),
        inset 0 1px 0 rgba(255,255,255,.18);
    transition: .25s ease !important;
}

.stButton > button:hover {
    transform: translateY(-3px);
    background-position: 100% 0 !important;
    box-shadow:
        0 20px 50px rgba(168,85,247,.38),
        0 0 30px rgba(236,72,153,.12);
}

/* ---------- scanner ---------- */

.scanner {
    position: relative;
    overflow: hidden;
    text-align: center;
    margin: 1.5rem 0;
    padding: 2.3rem 1rem;
    border-radius: 26px;
    background:
        radial-gradient(circle at 50% 40%, rgba(168,85,247,.12), transparent 40%),
        rgba(6,5,14,.83);
    border: 1px solid rgba(168,85,247,.22);
    box-shadow: 0 25px 70px rgba(0,0,0,.30);
}

.scanner::after {
    content: "";
    position: absolute;
    top: 0;
    left: 8%;
    right: 8%;
    height: 2px;
    background: linear-gradient(
        90deg,
        transparent,
        var(--cyan),
        var(--purple),
        var(--pink),
        transparent
    );
    box-shadow: 0 0 20px rgba(34,211,238,.8);
    animation: scan 2.2s ease-in-out infinite;
}

@keyframes scan {
    0% { transform: translateY(-120px); opacity: 0; }
    20%, 80% { opacity: 1; }
    100% { transform: translateY(220px); opacity: 0; }
}

.scanner-icon {
    font-size: 3rem;
    display: block;
    animation: scannerPulse 1.4s ease-in-out infinite;
}

@keyframes scannerPulse {
    50% {
        transform: scale(1.1);
        filter: drop-shadow(0 0 18px rgba(168,85,247,.65));
    }
}

.scanner-title {
    margin-top: .4rem;
    font-size: .75rem;
    font-weight: 900;
    letter-spacing: .16em;
    text-transform: uppercase;
}

.scanner-sub {
    color: #6d6676;
    margin-top: .4rem;
    font-size: .71rem;
}

/* ---------- result ---------- */

.result {
    padding: 1.6rem;
    border-radius: 28px;
    background:
        radial-gradient(circle at 50% 0%, rgba(168,85,247,.11), transparent 42%),
        rgba(7,5,17,.78);
    border: 1px solid rgba(255,255,255,.09);
    box-shadow:
        0 28px 90px rgba(0,0,0,.42),
        inset 0 1px 0 rgba(255,255,255,.04);
}

.scores {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    gap: 1rem;
    align-items: center;
    text-align: center;
}

.score-name {
    color: #c8bfda;
    font-size: .74rem;
    font-weight: 900;
    letter-spacing: .11em;
}

.score {
    margin: .15rem 0;
    font-family: "Space Grotesk", sans-serif;
    font-size: 3.3rem;
    font-weight: 900;
    background: linear-gradient(120deg, #ffffff, #c4b5fd, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.vs {
    width: 50px;
    height: 50px;
    display: grid;
    place-items: center;
    border-radius: 50%;
    color: var(--gold);
    font-size: .78rem;
    font-weight: 900;
    border: 1px solid rgba(250,204,21,.32);
    background: rgba(250,204,21,.06);
    box-shadow: 0 0 28px rgba(250,204,21,.11);
}

.metric {
    margin-top: 1.1rem;
}

.metric-top {
    display: flex;
    justify-content: space-between;
    color: #81798d;
    font-size: .69rem;
    font-weight: 800;
}

.track-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 5px;
    margin-top: .35rem;
}

.track {
    height: 9px;
    background: rgba(255,255,255,.055);
    border-radius: 999px;
    overflow: hidden;
}

.fill-a {
    height: 100%;
    background: linear-gradient(90deg, var(--cyan), var(--purple));
    border-radius: inherit;
    animation: fillBar 1s ease-out;
}

.fill-b {
    height: 100%;
    background: linear-gradient(90deg, var(--purple), var(--pink));
    border-radius: inherit;
    animation: fillBar 1s ease-out;
}

@keyframes fillBar {
    from { width: 0; }
}

/* ---------- reasoning ---------- */

.reason {
    height: 100%;
    padding: 1.25rem;
    border-radius: 22px;
    background: rgba(10,8,22,.74);
    border: 1px solid rgba(255,255,255,.08);
    box-shadow: 0 15px 45px rgba(0,0,0,.25);
}

.reason h3 {
    margin: 0 0 .7rem;
    font-size: .9rem;
    font-weight: 900;
}

.reason p {
    color: #a9a0b4 !important;
    text-align: left !important;
    line-height: 1.7;
    font-size: .82rem;
}

.tag {
    display: inline-block;
    margin: .3rem .25rem 0 0;
    padding: .4rem .62rem;
    border-radius: 999px;
    color: #fda4af;
    background: rgba(251,113,133,.07);
    border: 1px solid rgba(251,113,133,.24);
    font-size: .64rem;
    font-weight: 900;
}

.clean {
    color: #86efac;
    font-size: .72rem;
    font-weight: 800;
}

/* ---------- winner ---------- */

.winner {
    position: relative;
    overflow: hidden;
    margin-top: 1.4rem;
    padding: 2.7rem 1.4rem 2.2rem;
    text-align: center;
    border-radius: 32px;
    background:
        radial-gradient(circle at 50% 12%, rgba(250,204,21,.24), transparent 35%),
        radial-gradient(circle at 50% 100%, rgba(168,85,247,.10), transparent 45%),
        rgba(28,20,9,.88);
    border: 1px solid rgba(250,204,21,.42);
    box-shadow:
        0 25px 85px rgba(250,204,21,.12),
        inset 0 1px 0 rgba(255,255,255,.06);
    animation: winnerIn .8s cubic-bezier(.2,.8,.2,1);
}

.winner::before {
    content: "✦  ✧  ✦  ✧  ✦";
    position: absolute;
    top: 12px;
    left: 0;
    right: 0;
    color: rgba(250,204,21,.42);
    font-size: .63rem;
    letter-spacing: 1rem;
}

@keyframes winnerIn {
    from { opacity: 0; transform: translateY(30px) scale(.90); }
    to { opacity: 1; transform: none; }
}

.crown {
    display: block;
    font-size: 4rem;
    filter: drop-shadow(0 0 18px rgba(250,204,21,.55));
    animation: crownFloat 2s ease-in-out infinite;
}

@keyframes crownFloat {
    50% { transform: translateY(-9px) rotate(2deg); }
}

.winner h2 {
    margin: .4rem 0 0;
    color: var(--gold);
    font-family: "Space Grotesk", sans-serif;
    font-size: 2rem;
    font-weight: 900;
}

.winner-badge {
    display: inline-block;
    margin: .7rem 0;
    padding: .46rem .8rem;
    border-radius: 999px;
    color: #fff2b8;
    background: rgba(250,204,21,.08);
    border: 1px solid rgba(250,204,21,.22);
    font-size: .68rem;
    font-weight: 900;
}

.winner-reason {
    max-width: 760px;
    margin: 0 auto;
    color: #b8b0bc;
    line-height: 1.7;
    font-size: .83rem;
}

.footer-text {
    text-align: center;
    margin-top: 2rem;
    color: #4c4654;
    font-size: .61rem;
    font-weight: 800;
    letter-spacing: .15em;
    text-transform: uppercase;
}

@media (max-width: 700px) {
    .main .block-container {
        padding: 1rem;
    }

    .scores {
        grid-template-columns: 1fr;
    }

    .vs {
        margin: auto;
    }
}
</style>
"""

CSS = CSS.replace("background-image:linear-gradient(rgba(5,3,14,.80),rgba(5,3,14,.96));", background_css)
st.markdown(CSS, unsafe_allow_html=True)


# =========================================================
# AMBIENT BACKGROUND
# =========================================================

st.markdown(
    """
    <div class="bg-layer"></div>
    <div class="ambient">
        <span class="one"></span>
        <span class="two"></span>
        <span class="three"></span>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# INTRO
# Uses components.html so the intro can NEVER display raw HTML.
# =========================================================

if "entered" not in st.session_state:
    st.session_state.entered = False

if not st.session_state.entered:

    intro_html = r"""
    <!doctype html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            * { box-sizing: border-box; }
            html, body {
                margin: 0;
                width: 100%;
                height: 100%;
                overflow: hidden;
            }
            body {
                font-family: Arial, sans-serif;
                background:
                    radial-gradient(circle at 50% 35%, rgba(168,85,247,.20), transparent 32%),
                    radial-gradient(circle at 12% 75%, rgba(34,211,238,.08), transparent 25%),
                    radial-gradient(circle at 88% 20%, rgba(244,114,182,.08), transparent 24%),
                    linear-gradient(155deg, #100726, #04030b 72%);
                color: #f8fafc;
            }
            .wrap {
                width: 100%;
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .panel {
                position: relative;
                width: 94%;
                height: 94%;
                min-height: 650px;
                overflow: hidden;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 34px;
                border: 1px solid rgba(255,255,255,.10);
                background:
                    radial-gradient(circle at 50% 40%, rgba(168,85,247,.12), transparent 36%),
                    rgba(5,4,13,.80);
                box-shadow:
                    0 40px 120px rgba(0,0,0,.52),
                    inset 0 1px 0 rgba(255,255,255,.06);
            }
            .panel::before {
                content: "";
                position: absolute;
                inset: 18px;
                border: 1px solid rgba(168,85,247,.17);
                border-radius: 26px;
                pointer-events: none;
            }
            .grid {
                position: absolute;
                inset: 0;
                background:
                    linear-gradient(rgba(168,85,247,.04) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(168,85,247,.04) 1px, transparent 1px);
                background-size: 72px 72px;
                mask-image: radial-gradient(circle at center, black 0%, transparent 80%);
            }
            .orb {
                position: absolute;
                border-radius: 50%;
                filter: blur(70px);
                opacity: .20;
                animation: drift 13s ease-in-out infinite alternate;
            }
            .orb.one {
                width: 270px;
                height: 270px;
                left: -90px;
                top: -50px;
                background: #8b5cf6;
            }
            .orb.two {
                width: 230px;
                height: 230px;
                right: -60px;
                bottom: -60px;
                background: #22d3ee;
                animation-delay: -5s;
            }
            .orb.three {
                width: 180px;
                height: 180px;
                right: 22%;
                top: 7%;
                background: #ec4899;
                animation-delay: -9s;
            }
            @keyframes drift {
                from { transform: translate(0,0) scale(.9); }
                to { transform: translate(45px,-25px) scale(1.12); }
            }
            .corner {
                position: absolute;
                width: 88px;
                height: 88px;
                border-color: rgba(34,211,238,.21);
            }
            .tl {
                left: 28px;
                top: 28px;
                border-left: 2px solid;
                border-top: 2px solid;
                border-radius: 15px 0 0 0;
            }
            .tr {
                right: 28px;
                top: 28px;
                border-right: 2px solid;
                border-top: 2px solid;
                border-radius: 0 15px 0 0;
            }
            .bl {
                left: 28px;
                bottom: 28px;
                border-left: 2px solid;
                border-bottom: 2px solid;
                border-radius: 0 0 0 15px;
            }
            .br {
                right: 28px;
                bottom: 28px;
                border-right: 2px solid;
                border-bottom: 2px solid;
                border-radius: 0 0 15px 0;
            }
            .content {
                position: relative;
                z-index: 5;
                width: 82%;
                max-width: 840px;
                text-align: center;
            }
            .pill {
                display: inline-block;
                padding: 9px 18px;
                border-radius: 999px;
                border: 1px solid rgba(168,85,247,.32);
                background: rgba(168,85,247,.07);
                color: #ddd6fe;
                font-size: 10px;
                font-weight: 900;
                letter-spacing: 3px;
                text-transform: uppercase;
                animation: rise .8s both;
            }
            .team {
                margin-top: 24px;
                color: white;
                font-size: 16px;
                font-weight: 900;
                letter-spacing: 10px;
                padding-left: 10px;
                text-shadow: 0 0 30px rgba(168,85,247,.45);
                animation: rise .9s .08s both;
            }
            .title {
                margin-top: 22px;
                font-size: clamp(55px, 10vw, 116px);
                line-height: .82;
                font-weight: 900;
                letter-spacing: -7px;
                background: linear-gradient(
                    100deg,
                    #ffffff,
                    #ddd6fe,
                    #a855f7,
                    #f472b6,
                    #22d3ee,
                    #ffffff
                );
                background-size: 300% auto;
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                animation: rise 1s .14s both, shine 7s linear infinite;
            }
            @keyframes shine {
                to { background-position: 300% 50%; }
            }
            .sub {
                margin-top: 20px;
                color: #b7afc2;
                font-size: 11px;
                font-weight: 800;
                letter-spacing: 5px;
                text-transform: uppercase;
                animation: rise 1s .23s both;
            }
            .line {
                width: 230px;
                height: 2px;
                margin: 24px auto;
                background: linear-gradient(
                    90deg,
                    transparent,
                    #22d3ee,
                    #a855f7,
                    #f472b6,
                    transparent
                );
                box-shadow: 0 0 22px rgba(168,85,247,.60);
                animation: pulse 2.4s ease-in-out infinite;
            }
            .desc {
                max-width: 620px;
                margin: 0 auto;
                color: #81798c;
                font-size: 13px;
                line-height: 1.8;
                animation: rise 1s .32s both;
            }
            .cards {
                display: flex;
                justify-content: center;
                flex-wrap: wrap;
                gap: 12px;
                margin-top: 28px;
                animation: rise 1s .40s both;
            }
            .card {
                min-width: 145px;
                padding: 14px 16px;
                border-radius: 17px;
                background: rgba(255,255,255,.025);
                border: 1px solid rgba(255,255,255,.08);
                box-shadow: 0 12px 30px rgba(0,0,0,.25);
            }
            .card strong {
                display: block;
                color: white;
                font-size: 11px;
                font-weight: 900;
            }
            .card span {
                display: block;
                margin-top: 5px;
                color: #625b6d;
                font-size: 8px;
                font-weight: 800;
                letter-spacing: 2px;
                text-transform: uppercase;
            }
            .status {
                margin-top: 25px;
                color: #5d5668;
                font-size: 8px;
                font-weight: 900;
                letter-spacing: 2px;
                text-transform: uppercase;
                animation: rise 1s .48s both;
            }
            .dot {
                display: inline-block;
                width: 7px;
                height: 7px;
                margin-right: 6px;
                border-radius: 50%;
                background: #4ade80;
                box-shadow: 0 0 10px #4ade80;
                animation: beat 1.4s infinite;
                vertical-align: middle;
            }
            .spark {
                position: absolute;
                z-index: 6;
                color: white;
                opacity: .45;
                font-size: 14px;
                animation: float 3.5s ease-in-out infinite;
            }
            .s1 { left: 13%; top: 25%; }
            .s2 { right: 14%; top: 28%; animation-delay: -1s; }
            .s3 { left: 18%; bottom: 22%; animation-delay: -2s; }
            .s4 { right: 18%; bottom: 20%; animation-delay: -.5s; }
            @keyframes float {
                50% {
                    transform: translateY(-16px) rotate(8deg);
                    opacity: .9;
                }
            }
            @keyframes rise {
                from {
                    opacity: 0;
                    transform: translateY(24px) scale(.98);
                }
                to {
                    opacity: 1;
                    transform: none;
                }
            }
            @keyframes pulse {
                0%,100% { opacity: .45; transform: scaleX(.8); }
                50% { opacity: 1; transform: scaleX(1); }
            }
            @keyframes beat {
                50% { transform: scale(1.35); opacity: .75; }
            }
        </style>
    </head>
    <body>
        <div class="wrap">
            <div class="panel">
                <div class="grid"></div>
                <div class="orb one"></div>
                <div class="orb two"></div>
                <div class="orb three"></div>

                <div class="corner tl"></div>
                <div class="corner tr"></div>
                <div class="corner bl"></div>
                <div class="corner br"></div>

                <div class="spark s1">✦</div>
                <div class="spark s2">◇</div>
                <div class="spark s3">✧</div>
                <div class="spark s4">⚡</div>

                <div class="content">
                    <div class="pill">⚡ HACK TITANS · AI DEBATE ARENA</div>
                    <div class="team">HACK TITANS</div>
                    <div class="title">FALLACY<br>FINDER</div>
                    <div class="sub">🧠 AI-POWERED LOGIC INTELLIGENCE</div>
                    <div class="line"></div>

                    <div class="desc">
                        Discover weak reasoning, expose hidden logical fallacies,
                        compare two arguments and let AI choose the stronger case.
                    </div>

                    <div class="cards">
                        <div class="card">
                            <strong>🧠 AI JUDGE</strong>
                            <span>Smart Analysis</span>
                        </div>
                        <div class="card">
                            <strong>⚠️ FALLACY SCAN</strong>
                            <span>Logic Detection</span>
                        </div>
                        <div class="card">
                            <strong>🏆 AI VERDICT</strong>
                            <span>Fair Decision</span>
                        </div>
                    </div>

                    <div class="status">
                        <span class="dot"></span>
                        AI ENGINE READY &nbsp;•&nbsp; SYSTEM ONLINE
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    components.html(
        intro_html,
        height=710,
        scrolling=False,
    )

    st.write("")
    _, center, _ = st.columns([1, 1.35, 1])

    with center:
        if st.button(
            "🚀  ENTER THE DEBATE ARENA",
            use_container_width=True,
            key="intro_enter_final_fixed",
        ):
            st.session_state.entered = True
            st.rerun()

    st.stop()


# =========================================================
# MAIN APP
# =========================================================

st.markdown(
    """
    <div class="brand">
        <span class="brand-dot"></span>
        <span class="brand-name">HACK TITANS</span>
        <span class="brand-small">AI DEBATE LAB</span>
    </div>

    <div class="hero-title">🔍 FALLACY FINDER</div>
    <div class="hero-sub">AI-powered debate intelligence</div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section">📝 CREATE YOUR DEBATE</div>',
    unsafe_allow_html=True,
)

topic = st.text_input(
    "Debate Topic",
    placeholder="Example: School la uniform kandippa venuma?",
    key="topic_final",
)

left, right = st.columns(2, gap="large")

with left:
    st.markdown(
        '<div class="arg arg-a">🔵 SIDE A</div>',
        unsafe_allow_html=True,
    )
    argument_a = st.text_area(
        "Argument A",
        placeholder="Unga argument Tanglish or English la type pannunga...",
        height=170,
        label_visibility="collapsed",
        key="argument_a_final",
    )

with right:
    st.markdown(
        '<div class="arg arg-b">🟣 SIDE B</div>',
        unsafe_allow_html=True,
    )
    argument_b = st.text_area(
        "Argument B",
        placeholder="Counter argument Tanglish or English la type pannunga...",
        height=170,
        label_visibility="collapsed",
        key="argument_b_final",
    )

st.write("")

submitted = st.button(
    "🚀  ANALYZE ARGUMENTS",
    use_container_width=True,
    key="analyze_final",
)

if submitted:

    if not topic.strip() or not argument_a.strip() or not argument_b.strip():
        st.warning("⚠️ Please enter the topic and both arguments.")
        st.stop()

    scan = st.empty()

    scan.markdown(
        """
        <div class="scanner">
            <div class="scanner-icon">🧠</div>
            <div class="scanner-title">AI IS ANALYZING</div>
            <div class="scanner-sub">
                🔍 Logic &nbsp;·&nbsp; 📚 Evidence &nbsp;·&nbsp; ⚠️ Fallacies &nbsp;·&nbsp; 🏆 Verdict
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        result = judge_arguments(topic, argument_a, argument_b)
        time.sleep(.7)
    except Exception as exc:
        scan.empty()
        st.error("❌ Gemini analysis failed")
        st.code(str(exc), language="text")
        st.info(
            "Check: 1) GEMINI_API_KEY in Streamlit Cloud Secrets, "
            "2) requirements.txt contains google-genai, "
            "3) the app has been redeployed after changing Secrets."
        )
        st.stop()

    scan.empty()

    a = result["argument_a"]
    b = result["argument_b"]

    total_a = int(a["logic"]) + int(a["evidence"]) + int(a["persuasiveness"])
    total_b = int(b["logic"]) + int(b["evidence"]) + int(b["persuasiveness"])

    winner = str(result["winner"]).strip().upper()
    if winner not in {"A", "B"}:
        winner = "A" if total_a >= total_b else "B"

    winner_total = total_a if winner == "A" else total_b

    def esc(value):
        return html.escape(str(value))

    def fallacy_html(items):
        if not items:
            return '<span class="clean">✨ No fallacies detected</span>'
        return "".join(
            f'<span class="tag">⚠️ {esc(item)}</span>'
            for item in items
        )

    metric_rows = ""

    for label, value_a, value_b in [
        ("🧠 LOGIC", int(a["logic"]), int(b["logic"])),
        ("📚 EVIDENCE", int(a["evidence"]), int(b["evidence"])),
        ("💬 PERSUASIVENESS", int(a["persuasiveness"]), int(b["persuasiveness"])),
    ]:
        metric_rows += f"""
        <div class="metric">
            <div class="metric-top">
                <span>{label}</span>
                <span>{value_a}/10&nbsp;&nbsp;&nbsp;{value_b}/10</span>
            </div>
            <div class="track-row">
                <div class="track">
                    <div class="fill-a" style="width:{value_a * 10}%"></div>
                </div>
                <div class="track">
                    <div class="fill-b" style="width:{value_b * 10}%"></div>
                </div>
            </div>
        </div>
        """

    st.markdown(
        '<div class="section">🧠 AI VERDICT</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="result">
            <div class="scores">
                <div>
                    <div class="score-name">🔵 SIDE A</div>
                    <div class="score">{total_a}</div>
                    <div style="color:#5f5868;font-size:.62rem;letter-spacing:.12em;">
                        OUT OF 30
                    </div>
                </div>

                <div class="vs">VS</div>

                <div>
                    <div class="score-name">🟣 SIDE B</div>
                    <div class="score">{total_b}</div>
                    <div style="color:#5f5868;font-size:.62rem;letter-spacing:.12em;">
                        OUT OF 30
                    </div>
                </div>
            </div>

            {metric_rows}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section">⚠️ FALLACY DETECTION</div>',
        unsafe_allow_html=True,
    )

    ca, cb = st.columns(2, gap="large")

    with ca:
        st.markdown(
            f"""
            <div class="reason">
                <h3>🔵 Side A</h3>
                <p>{esc(a["reason"])}</p>
                {fallacy_html(a["fallacies"])}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with cb:
        st.markdown(
            f"""
            <div class="reason">
                <h3>🟣 Side B</h3>
                <p>{esc(b["reason"])}</p>
                {fallacy_html(b["fallacies"])}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="section">👑 FINAL DECISION</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="winner">
            <span class="crown">👑</span>
            <h2>🏆 SIDE {esc(winner)} WINS</h2>
            <div class="winner-badge">
                ⚡ {winner_total} / 30 · STRONGER ARGUMENT
            </div>
            <div class="winner-reason">
                {esc(result["overall_reason"])}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="footer-text">HACK TITANS · FALLACY FINDER</div>',
    unsafe_allow_html=True,
)
