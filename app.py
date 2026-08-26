import streamlit as st
import google.generativeai as genai
import os
import json
import time
import base64

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-3.6-flash")


def judge_arguments(topic, argument_a, argument_b):
    prompt = (
        "You are an impartial debate judge and logical fallacy expert.\n\n"
        "The topic and arguments may be written in Tanglish (Tamil words spelled out "
        "in English/Roman letters, often mixed with English words). Understand Tanglish "
        "input naturally, the same way a bilingual Tamil-English speaker would, and judge "
        "it fairly regardless of language mixing or spelling variations.\n\n"
        f"Topic: {topic}\n\n"
        f"Argument A: {argument_a}\n\n"
        f"Argument B: {argument_b}\n\n"
        "Judge only the strength of reasoning and evidence in the text itself. "
        "Do not favor either side based on argument length, order, or writing style alone.\n\n"
        "Evaluate both arguments on: logic, evidence, and persuasiveness (each scored 0-10). "
        "Also identify any logical fallacies present in each argument. If none are present, return an empty list.\n\n"
        "Write the 'reason' and 'overall_reason' fields in simple Tanglish (Tamil mixed with "
        "English, written in English letters) so a Tamil speaker finds it natural and easy to "
        "read — for example, style like: 'Argument A logic ku evidence support pannala, "
        "but Argument B reasoning konjam strong ah irukku.' Keep fallacy names themselves in English "
        "(e.g. 'ad hominem', 'strawman') since those are standard terms, but explain them in Tanglish.\n\n"
        "Respond ONLY with valid JSON in exactly this format, no other text:\n\n"
        "{\n"
        '  "argument_a": {"logic": 0, "evidence": 0, "persuasiveness": 0, "reason": "text", "fallacies": []},\n'
        '  "argument_b": {"logic": 0, "evidence": 0, "persuasiveness": 0, "reason": "text", "fallacies": []},\n'
        '  "winner": "A or B",\n'
        '  "overall_reason": "text"\n'
        "}"
    )
    response = model.generate_content(prompt)
    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text)


@st.cache_data
def get_base64_bg(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# ============ PAGE SETUP ============
st.set_page_config(page_title="Fallacy Finder", page_icon="🔍", layout="centered")

bg_base64 = get_base64_bg("assets/background.jpg")

GLOBAL_CSS = f"""
<style>
@keyframes glowPulse {{
    0%, 100% {{ text-shadow: 0 0 20px rgba(244,114,182,0.8), 0 0 40px rgba(168,85,247,0.5); }}
    50% {{ text-shadow: 0 0 30px rgba(250,204,21,0.9), 0 0 60px rgba(244,114,182,0.6); }}
}}
@keyframes popIn {{
    0% {{ opacity: 0; transform: scale(0.7) translateY(40px); }}
    60% {{ opacity: 1; transform: scale(1.05) translateY(-8px); }}
    100% {{ opacity: 1; transform: scale(1) translateY(0); }}
}}
@keyframes searchSweep {{
    0% {{ transform: translate(0,0) rotate(0deg); }}
    25% {{ transform: translate(50px,-15px) rotate(12deg); }}
    50% {{ transform: translate(-35px,20px) rotate(-10deg); }}
    75% {{ transform: translate(35px,30px) rotate(8deg); }}
    100% {{ transform: translate(0,0) rotate(0deg); }}
}}
@keyframes fillBar {{
    from {{ width: 0%; }}
}}
@keyframes crownDrop {{
    0% {{ opacity: 0; transform: translateY(-30px) scale(0.5); }}
    60% {{ opacity: 1; transform: translateY(5px) scale(1.1); }}
    100% {{ opacity: 1; transform: translateY(0) scale(1); }}
}}
@keyframes kenBurns {{
    0% {{ transform: scale(1) translate(0, 0); }}
    50% {{ transform: scale(1.12) translate(-1.5%, -1%); }}
    100% {{ transform: scale(1) translate(0, 0); }}
}}
.stApp {{
    background: #0a0614;
}}
.bg-layer {{
    position: fixed;
    top: -5%; left: -5%; width: 110%; height: 110%;
    background-image: url("data:image/jpg;base64,{bg_base64}");
    background-size: cover;
    background-position: center;
    animation: kenBurns 22s ease-in-out infinite;
    z-index: -2;
}}
.bg-tint {{
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    background: linear-gradient(180deg, rgba(10,6,20,0.55), rgba(10,6,20,0.7));
    z-index: -1;
}}
.block-container {{
    position: relative;
    z-index: 1;
}}
.particle-layer {{
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    pointer-events: none;
    overflow: hidden;
    z-index: 0;
}}
.particle {{
    position: absolute;
    font-size: 1.3em;
    animation: floatUp linear infinite;
    opacity: 0;
}}
@keyframes floatUp {{
    0% {{ transform: translateY(0) rotate(0deg); opacity: 0; }}
    10% {{ opacity: 0.9; }}
    90% {{ opacity: 0.9; }}
    100% {{ transform: translateY(-105vh) rotate(360deg); opacity: 0; }}
}}
.team-banner {{
    text-align: center;
    font-size: 2.6em;
    font-weight: 900;
    letter-spacing: 10px;
    color: #ffffff;
    animation: glowPulse 3s ease-in-out infinite;
    margin-bottom: 0;
}}
.team-sub {{
    text-align: center;
    color: #e9d5ff;
    font-size: 0.85em;
    letter-spacing: 5px;
    margin-bottom: 1.2em;
    opacity: 0.85;
}}
h1 {{
    text-align: center;
    background: linear-gradient(90deg, #f472b6, #a855f7, #facc15);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    font-size: 2.8em !important;
}}
.stCaption, p {{
    text-align: center;
    color: #e9d5ff !important;
}}
div[data-testid="stForm"] {{
    background: rgba(15,10,25,0.55);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 22px;
    padding: 2em;
    box-shadow: 0 8px 40px rgba(0,0,0,0.4);
}}
.stTextArea textarea, .stTextInput input {{
    background: rgba(255,255,255,0.08) !important;
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    color: white !important;
}}
.stTextArea textarea:focus, .stTextInput input:focus {{
    border: 1px solid #f472b6 !important;
    box-shadow: 0 0 18px rgba(244,114,182,0.6) !important;
}}
.stButton>button {{
    width: 100%;
    border-radius: 14px;
    height: 3.3em;
    font-weight: 700;
    font-size: 1.05em;
    background: linear-gradient(90deg, #f472b6, #a855f7, #facc15);
    background-size: 200% 200%;
    color: white;
    border: none;
    box-shadow: 0 4px 25px rgba(168,85,247,0.5);
}}
.stButton>button:hover {{
    transform: scale(1.02);
}}
.search-wrap {{
    text-align: center;
    padding: 2.5em 1em;
}}
.magnifier {{
    font-size: 4em;
    display: inline-block;
    animation: searchSweep 2s ease-in-out infinite;
}}
.search-caption {{
    color: #e9d5ff;
    font-size: 1.05em;
    margin-top: 0.8em;
    letter-spacing: 2px;
}}

/* ---------- PRO SCOREBOARD ---------- */
.scoreboard {{
    animation: popIn 0.6s ease-out;
    background: rgba(15,10,28,0.6);
    backdrop-filter: blur(18px);
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: 24px;
    padding: 1.8em;
    box-shadow: 0 12px 45px rgba(0,0,0,0.45);
    margin-bottom: 1.2em;
}}
.vs-header {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1.2em;
    margin-bottom: 1.4em;
}}
.vs-side {{
    flex: 1;
    text-align: center;
}}
.vs-name {{
    font-size: 1.3em;
    font-weight: 800;
    color: white;
}}
.vs-total {{
    font-size: 2.2em;
    font-weight: 900;
    background: linear-gradient(90deg, #f472b6, #facc15);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}
.vs-badge {{
    font-size: 1.1em;
    font-weight: 900;
    color: #facc15;
    letter-spacing: 2px;
    padding: 0.4em 0.7em;
    border: 1px solid rgba(250,204,21,0.4);
    border-radius: 50%;
}}
.metric-row {{
    margin-bottom: 1em;
}}
.metric-label {{
    display: flex;
    justify-content: space-between;
    color: #e9d5ff;
    font-size: 0.85em;
    margin-bottom: 0.3em;
    letter-spacing: 1px;
}}
.bar-track {{
    display: flex;
    align-items: center;
    gap: 0.6em;
}}
.bar-bg {{
    flex: 1;
    height: 10px;
    background: rgba(255,255,255,0.08);
    border-radius: 6px;
    overflow: hidden;
    position: relative;
}}
.bar-fill-a {{
    height: 100%;
    border-radius: 6px;
    background: linear-gradient(90deg, #f472b6, #a855f7);
    animation: fillBar 1s ease-out;
    box-shadow: 0 0 10px rgba(244,114,182,0.7);
}}
.bar-fill-b {{
    height: 100%;
    border-radius: 6px;
    background: linear-gradient(90deg, #a855f7, #facc15);
    animation: fillBar 1s ease-out;
    box-shadow: 0 0 10px rgba(168,85,247,0.7);
    margin-left: auto;
}}
.bar-value {{
    color: white;
    font-size: 0.8em;
    font-weight: 700;
    width: 2.4em;
}}
.reason-card {{
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 16px;
    padding: 1.1em;
    margin-bottom: 0.8em;
    height: 100%;
}}
.reason-title {{
    font-weight: 700;
    color: #facc15;
    margin-bottom: 0.4em;
}}
.tag {{
    display: inline-block;
    background: rgba(248,113,113,0.15);
    color: #fca5a5;
    border: 1px solid rgba(248,113,113,0.4);
    padding: 4px 12px;
    border-radius: 14px;
    font-size: 0.78em;
    margin: 3px 4px 0 0;
}}
.clean-tag {{
    color: #86efac;
    font-size: 0.85em;
}}
.winner-box {{
    text-align: center;
    background: rgba(250,204,21,0.12);
    border: 1px solid rgba(250,204,21,0.5);
    border-radius: 20px;
    padding: 1.4em;
    margin-top: 0.4em;
    box-shadow: 0 8px 35px rgba(250,204,21,0.25);
}}
.crown {{
    font-size: 2.2em;
    display: block;
    animation: crownDrop 0.8s ease-out;
}}
.winner-title {{
    font-size: 1.5em;
    font-weight: 800;
    background: linear-gradient(90deg, #facc15, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 2px;
}}
.intro-wrap {{
    text-align: center;
    padding-top: 8vh;
}}
.intro-team {{
    font-size: 3.2em;
    font-weight: 900;
    letter-spacing: 14px;
    color: #ffffff;
    animation: glowPulse 2.5s ease-in-out infinite;
}}
.intro-sub {{
    color: #e9d5ff;
    letter-spacing: 4px;
    margin-top: 0.6em;
    font-size: 1.1em;
    opacity: 0.9;
}}
</style>
"""

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

BG_LAYERS_HTML = """
<div class="bg-layer"></div>
<div class="bg-tint"></div>
<div class="particle-layer">
<div class="particle" style="left:6%; animation-duration:14s; animation-delay:0s;">&#10024;</div>
<div class="particle" style="left:16%; animation-duration:18s; animation-delay:3s;">&#11088;</div>
<div class="particle" style="left:28%; animation-duration:16s; animation-delay:1s;">&#128269;</div>
<div class="particle" style="left:40%; animation-duration:20s; animation-delay:5s;">&#128171;</div>
<div class="particle" style="left:52%; animation-duration:15s; animation-delay:2s;">&#10024;</div>
<div class="particle" style="left:64%; animation-duration:19s; animation-delay:4s;">&#11088;</div>
<div class="particle" style="left:76%; animation-duration:17s; animation-delay:0.5s;">&#9888;</div>
<div class="particle" style="left:88%; animation-duration:21s; animation-delay:6s;">&#128269;</div>
<div class="particle" style="left:96%; animation-duration:14s; animation-delay:2.5s;">&#10024;</div>
<div class="particle" style="left:20%; animation-duration:22s; animation-delay:7s;">&#11088;</div>
</div>
"""
st.markdown(BG_LAYERS_HTML, unsafe_allow_html=True)

# ============ INTRO SCREEN ============
if "entered" not in st.session_state:
    st.session_state.entered = False

if not st.session_state.entered:
    st.markdown(
        '<div class="intro-wrap">'
        '<div style="font-size:1em; letter-spacing:6px; color:#facc15;">PRESENTING</div>'
        '<div class="intro-team">HACK TITANS</div>'
        '<div class="intro-sub">🔍 FALLACY FINDER — AI DEBATE JUDGE 🔍</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.write("")
    st.write("")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("✨ Enter the App"):
            st.session_state.entered = True
            st.rerun()
    st.stop()

# ============ MAIN APP ============
st.markdown('<div class="team-banner">HACK TITANS</div>', unsafe_allow_html=True)
st.markdown('<div class="team-sub">PRESENTS</div>', unsafe_allow_html=True)
st.title("🔍 Fallacy Finder")
st.caption("Spot weak logic and score arguments fairly, powered by AI.")
st.caption("🇮🇳 Tanglish-la type pannalam — English or Tamil (Roman letters) both work!")

with st.form("judge_form"):
    topic = st.text_input("Debate Topic", placeholder="Eg: School la uniform kandippa venuma?")
    col1, col2 = st.columns(2)
    with col1:
        argument_a = st.text_area("Argument A", placeholder="Unga argument Tanglish or English la type pannunga...", height=150)
    with col2:
        argument_b = st.text_area("Argument B", placeholder="Type your argument in Tanglish or English...", height=150)
    submitted = st.form_submit_button("🔍 Find the Fallacies")


def bar_row(label, val_a, val_b, max_val=10):
    pct_a = int((val_a / max_val) * 100)
    pct_b = int((val_b / max_val) * 100)
    return (
        '<div class="metric-row">'
        f'<div class="metric-label"><span>{val_a}</span><span>{label}</span><span>{val_b}</span></div>'
        '<div class="bar-track">'
        f'<div class="bar-value" style="text-align:right;">A</div>'
        f'<div class="bar-bg"><div class="bar-fill-a" style="width:{pct_a}%;"></div></div>'
        f'<div class="bar-bg"><div class="bar-fill-b" style="width:{pct_b}%;"></div></div>'
        f'<div class="bar-value">B</div>'
        '</div>'
        '</div>'
    )


if submitted:
    if not topic or not argument_a or not argument_b:
        st.warning("Please fill in the topic and both arguments.")
    else:
        search_box = st.empty()
        search_box.markdown(
            '<div class="search-wrap">'
            '<div class="magnifier">🔍</div>'
            '<div class="search-caption">Scanning arguments for logical fallacies...</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        result = judge_arguments(topic, argument_a, argument_b)
        time.sleep(1.6)
        search_box.empty()

        a = result["argument_a"]
        b = result["argument_b"]
        total_a = a["logic"] + a["evidence"] + a["persuasiveness"]
        total_b = b["logic"] + b["evidence"] + b["persuasiveness"]

        bars_html = (
            bar_row("LOGIC", a["logic"], b["logic"])
            + bar_row("EVIDENCE", a["evidence"], b["evidence"])
            + bar_row("PERSUASION", a["persuasiveness"], b["persuasiveness"])
        )

        scoreboard_html = (
            '<div class="scoreboard">'
            '<div class="vs-header">'
            '<div class="vs-side">'
            '<div class="vs-name">Argument A</div>'
            f'<div class="vs-total">{total_a}</div>'
            '<div style="color:#c4b5fd; font-size:0.75em;">out of 30</div>'
            '</div>'
            '<div class="vs-badge">VS</div>'
            '<div class="vs-side">'
            '<div class="vs-name">Argument B</div>'
            f'<div class="vs-total">{total_b}</div>'
            '<div style="color:#c4b5fd; font-size:0.75em;">out of 30</div>'
            '</div>'
            '</div>'
            + bars_html +
            '</div>'
        )
        st.markdown(scoreboard_html, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            fallacy_html = (
                '<div class="tags">' + "".join(f'<span class="tag">⚠ {f}</span>' for f in a["fallacies"]) + '</div>'
                if a["fallacies"] else '<div class="clean-tag">✨ No fallacies found</div>'
            )
            st.markdown(
                '<div class="reason-card">'
                '<div class="reason-title">Argument A — Reasoning</div>'
                f'<div>{a["reason"]}</div>'
                f'{fallacy_html}'
                '</div>',
                unsafe_allow_html=True,
            )
        with col2:
            fallacy_html_b = (
                '<div class="tags">' + "".join(f'<span class="tag">⚠ {f}</span>' for f in b["fallacies"]) + '</div>'
                if b["fallacies"] else '<div class="clean-tag">✨ No fallacies found</div>'
            )
            st.markdown(
                '<div class="reason-card">'
                '<div class="reason-title">Argument B — Reasoning</div>'
                f'<div>{b["reason"]}</div>'
                f'{fallacy_html_b}'
                '</div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            '<div class="winner-box">'
            '<span class="crown">🏆</span>'
            f'<div class="winner-title">Winner: Argument {result["winner"]}</div>'
            f'<div style="color:#e9d5ff; margin-top:0.5em;">{result["overall_reason"]}</div>'
            '</div>',
            unsafe_allow_html=True,
        )
