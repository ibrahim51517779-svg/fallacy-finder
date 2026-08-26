import streamlit as st
import google.generativeai as genai
import os
import json
import time
import base64
import html

# =========================================================
# ⚡ FALLACY FINDER — HACK TITANS
# Futuristic AI Debate Arena UI
# =========================================================

st.set_page_config(
    page_title="Fallacy Finder | Hack Titans",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -------------------- AI --------------------
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
        "English, written in English letters) so a Tamil speaker finds it natural and easy "
        "to read. Keep fallacy names themselves in English.\n\n"
        "Respond ONLY with valid JSON in exactly this format:\n\n"
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
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.startswith("json"):
            text = text[4:]

    return json.loads(text)


# -------------------- Background --------------------
@st.cache_data
def get_base64_bg(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return ""


bg_base64 = get_base64_bg("assets/background.jpg")

bg_image = (
    f'background-image:url("data:image/jpg;base64,{bg_base64}");'
    if bg_base64
    else ""
)

# -------------------- Premium CSS --------------------
GLOBAL_CSS = f"""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Space+Grotesk:wght@500;600;700&display=swap');

:root {{
    --bg: #05030d;
    --panel: rgba(13, 10, 27, .72);
    --panel-strong: rgba(16, 11, 33, .90);
    --white: #f8fafc;
    --muted: #a7a1bc;
    --purple: #a855f7;
    --pink: #f472b6;
    --cyan: #22d3ee;
    --gold: #facc15;
    --green: #4ade80;
    --red: #fb7185;
}}

* {{
    box-sizing: border-box;
}}

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

.stApp {{
    background:
        radial-gradient(circle at 15% 15%, rgba(168,85,247,.15), transparent 28%),
        radial-gradient(circle at 85% 25%, rgba(34,211,238,.10), transparent 25%),
        radial-gradient(circle at 50% 90%, rgba(244,114,182,.10), transparent 30%),
        #05030d;
    color: var(--white);
}}

header[data-testid="stHeader"] {{
    background: transparent !important;
}}

[data-testid="stAppViewContainer"] {{
    background: transparent;
}}

.main .block-container {{
    max-width: 1250px;
    padding: 2rem 2rem 5rem;
    position: relative;
    z-index: 2;
}}

footer {{
    visibility: hidden;
}}

#MainMenu {{
    visibility: hidden;
}}

/* ---------- Ambient background ---------- */

.bg-layer {{
    position: fixed;
    inset: -8%;
    width: 116%;
    height: 116%;
    background-image:
        linear-gradient(rgba(5,3,13,.62), rgba(5,3,13,.82)),
        {bg_image};
    background-size: cover;
    background-position: center;
    filter: saturate(1.15);
    animation: kenBurns 25s ease-in-out infinite;
    z-index: -5;
}}

.aurora {{
    position: fixed;
    inset: 0;
    overflow: hidden;
    pointer-events: none;
    z-index: -4;
}}

.orb {{
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
    opacity: .20;
    animation: drift 18s ease-in-out infinite alternate;
}}

.orb.one {{
    width: 360px; height: 360px;
    background: var(--purple);
    left: -100px; top: 5%;
}}

.orb.two {{
    width: 300px; height: 300px;
    background: var(--cyan);
    right: -80px; top: 25%;
    animation-delay: -6s;
}}

.orb.three {{
    width: 320px; height: 320px;
    background: var(--pink);
    left: 38%; bottom: -140px;
    animation-delay: -11s;
}}

.grid {{
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: -3;
    opacity: .13;
    background-image:
        linear-gradient(rgba(168,85,247,.18) 1px, transparent 1px),
        linear-gradient(90deg, rgba(168,85,247,.18) 1px, transparent 1px);
    background-size: 55px 55px;
    mask-image: linear-gradient(to bottom, black, transparent 88%);
}}

@keyframes kenBurns {{
    0%,100% {{ transform: scale(1); }}
    50% {{ transform: scale(1.08) translate(-1%, -1%); }}
}}

@keyframes drift {{
    from {{ transform: translate3d(0,0,0) scale(1); }}
    to {{ transform: translate3d(70px,-45px,0) scale(1.18); }}
}}

@keyframes pulse {{
    0%,100% {{ opacity: .55; transform: scale(.95); }}
    50% {{ opacity: 1; transform: scale(1.08); }}
}}

@keyframes shimmer {{
    0% {{ background-position: -300% 0; }}
    100% {{ background-position: 300% 0; }}
}}

@keyframes float {{
    0%,100% {{ transform: translateY(0) rotate(0deg); }}
    50% {{ transform: translateY(-18px) rotate(5deg); }}
}}

@keyframes scan {{
    0% {{ transform: translateY(-150%); opacity: 0; }}
    15%,85% {{ opacity: 1; }}
    100% {{ transform: translateY(150%); opacity: 0; }}
}}

@keyframes bar {{
    from {{ width: 0; }}
}}

@keyframes winner {{
    0% {{ opacity: 0; transform: translateY(25px) scale(.92); }}
    70% {{ transform: translateY(-4px) scale(1.02); }}
    100% {{ opacity: 1; transform: translateY(0) scale(1); }}
}}

/* ---------- Hero ---------- */

.hero {{
    text-align: center;
    padding: 3rem 1rem 2rem;
}}

.hero-kicker {{
    display: inline-flex;
    align-items: center;
    gap: .55rem;
    padding: .55rem 1rem;
    border-radius: 999px;
    border: 1px solid rgba(168,85,247,.35);
    background: rgba(168,85,247,.08);
    color: #ddd6fe;
    font-size: .76rem;
    font-weight: 800;
    letter-spacing: .18em;
    text-transform: uppercase;
    box-shadow: 0 0 30px rgba(168,85,247,.12);
}}

.hero-title {{
    margin: 1.1rem 0 .35rem;
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(3rem, 7vw, 6.5rem);
    line-height: .92;
    font-weight: 900;
    letter-spacing: -.065em;
    background: linear-gradient(110deg, #fff 0%, #ddd6fe 25%, #f472b6 52%, #a855f7 76%, #22d3ee 100%);
    background-size: 250% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmer 7s linear infinite;
}}

.hero-sub {{
    color: #aaa3bd;
    font-size: 1rem;
    letter-spacing: .12em;
    text-transform: uppercase;
}}

.hero-line {{
    width: 180px;
    height: 2px;
    margin: 1.35rem auto;
    background: linear-gradient(90deg, transparent, var(--purple), var(--cyan), transparent);
    box-shadow: 0 0 18px rgba(168,85,247,.7);
}}

/* ---------- Section headers ---------- */

.section-label {{
    display: flex;
    align-items: center;
    gap: .7rem;
    margin: 1.6rem 0 .8rem;
    color: #ddd6fe;
    font-size: .74rem;
    font-weight: 900;
    letter-spacing: .16em;
    text-transform: uppercase;
}}

.section-label::after {{
    content: "";
    height: 1px;
    flex: 1;
    background: linear-gradient(90deg, rgba(168,85,247,.4), transparent);
}}

/* ---------- Glass cards ---------- */

.glass {{
    position: relative;
    background: linear-gradient(145deg, rgba(22,17,40,.82), rgba(8,7,18,.70));
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 26px;
    box-shadow:
        0 25px 70px rgba(0,0,0,.40),
        inset 0 1px 0 rgba(255,255,255,.06);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
}}

.glass::before {{
    content: "";
    position: absolute;
    inset: 0;
    border-radius: inherit;
    padding: 1px;
    background: linear-gradient(135deg, rgba(168,85,247,.35), transparent 35%, transparent 65%, rgba(34,211,238,.18));
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    pointer-events: none;
}}

.topic-card {{
    padding: 1.5rem;
    margin-bottom: 1rem;
}}

.card-title {{
    font-weight: 800;
    font-size: 1rem;
    color: #fff;
    margin-bottom: .25rem;
}}

.card-sub {{
    color: #888198;
    font-size: .78rem;
}}

/* ---------- Streamlit inputs ---------- */

.stTextInput > div > div,
.stTextArea > div > div {{
    background: rgba(255,255,255,.035) !important;
    border: 1px solid rgba(255,255,255,.10) !important;
    border-radius: 16px !important;
    transition: .25s ease;
}}

.stTextInput > div > div:focus-within,
.stTextArea > div > div:focus-within {{
    border-color: rgba(168,85,247,.75) !important;
    box-shadow:
        0 0 0 3px rgba(168,85,247,.10),
        0 0 35px rgba(168,85,247,.13) !important;
    transform: translateY(-1px);
}}

.stTextInput input,
.stTextArea textarea {{
    color: #fff !important;
    background: transparent !important;
}}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {{
    color: #625c70 !important;
}}

label[data-testid="stWidgetLabel"] p {{
    color: #c4b5fd !important;
    font-weight: 700 !important;
    font-size: .78rem !important;
}}

.stTextArea textarea {{
    min-height: 155px;
}}

/* ---------- Buttons ---------- */

.stButton > button,
.stFormSubmitButton > button {{
    width: 100%;
    min-height: 52px;
    border: 0 !important;
    border-radius: 15px !important;
    color: white !important;
    font-weight: 900 !important;
    letter-spacing: .04em;
    background: linear-gradient(100deg, #7c3aed, #a855f7, #ec4899, #7c3aed) !important;
    background-size: 250% 100% !important;
    box-shadow:
        0 12px 35px rgba(168,85,247,.28),
        inset 0 1px 0 rgba(255,255,255,.18);
    transition: .25s ease !important;
}}

.stButton > button:hover,
.stFormSubmitButton > button:hover {{
    transform: translateY(-3px) scale(1.01);
    background-position: 100% 0 !important;
    box-shadow:
        0 18px 45px rgba(168,85,247,.42),
        0 0 30px rgba(236,72,153,.15);
}}

.stButton > button:active,
.stFormSubmitButton > button:active {{
    transform: translateY(0) scale(.99);
}}

/* ---------- Argument headers ---------- */

.arg-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: .7rem;
}}

.arg-pill {{
    display: inline-flex;
    align-items: center;
    gap: .45rem;
    padding: .45rem .7rem;
    border-radius: 999px;
    font-weight: 900;
    font-size: .73rem;
    letter-spacing: .08em;
}}

.arg-a {{
    background: rgba(34,211,238,.08);
    border: 1px solid rgba(34,211,238,.30);
    color: #67e8f9;
}}

.arg-b {{
    background: rgba(168,85,247,.10);
    border: 1px solid rgba(168,85,247,.32);
    color: #d8b4fe;
}}

/* ---------- Scanner ---------- */

.scanner {{
    position: relative;
    overflow: hidden;
    margin: 1.8rem 0;
    padding: 2.5rem 1rem;
    text-align: center;
    border-radius: 26px;
    background: rgba(8,7,18,.72);
    border: 1px solid rgba(168,85,247,.25);
    box-shadow: 0 20px 60px rgba(0,0,0,.35);
}}

.scanner::after {{
    content: "";
    position: absolute;
    left: 10%;
    right: 10%;
    height: 2px;
    top: 0;
    background: linear-gradient(90deg, transparent, var(--cyan), var(--purple), transparent);
    box-shadow: 0 0 22px rgba(34,211,238,.8);
    animation: scan 2.2s ease-in-out infinite;
}}

.scanner-icon {{
    font-size: 3.2rem;
    display: inline-block;
    animation: pulse 1.5s ease-in-out infinite;
}}

.scanner-title {{
    margin-top: .7rem;
    color: #fff;
    font-weight: 900;
    letter-spacing: .14em;
    text-transform: uppercase;
}}

.scanner-sub {{
    color: #81798e;
    font-size: .82rem;
    margin-top: .35rem;
}}

/* ---------- Scoreboard ---------- */

.scoreboard {{
    padding: 1.8rem;
    margin-top: 1rem;
    animation: winner .6s ease-out;
}}

.vs-grid {{
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    gap: 1rem;
    align-items: center;
}}

.score-side {{
    text-align: center;
    padding: 1rem;
}}

.score-name {{
    color: #c4b5fd;
    font-weight: 800;
    letter-spacing: .06em;
    font-size: .82rem;
}}

.score-number {{
    margin: .35rem 0;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 3.5rem;
    font-weight: 900;
    line-height: 1;
    background: linear-gradient(135deg, #fff, #c4b5fd, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

.score-max {{
    color: #666074;
    font-size: .7rem;
    text-transform: uppercase;
    letter-spacing: .15em;
}}

.vs {{
    width: 52px;
    height: 52px;
    display: grid;
    place-items: center;
    border-radius: 50%;
    color: #facc15;
    font-weight: 1000;
    font-size: .8rem;
    border: 1px solid rgba(250,204,21,.35);
    background: rgba(250,204,21,.07);
    box-shadow: 0 0 25px rgba(250,204,21,.12);
}}

.metric {{
    margin-top: 1.35rem;
}}

.metric-top {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: .45rem;
    color: #9f97ad;
    font-size: .74rem;
    font-weight: 700;
    letter-spacing: .07em;
}}

.metric-values {{
    color: #fff;
    font-weight: 900;
}}

.metric-track {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 5px;
}}

.track {{
    height: 10px;
    overflow: hidden;
    background: rgba(255,255,255,.055);
    border-radius: 999px;
}}

.fill-a {{
    height: 100%;
    border-radius: inherit;
    background: linear-gradient(90deg, var(--cyan), var(--purple));
    box-shadow: 0 0 15px rgba(168,85,247,.55);
    animation: bar 1s ease-out;
}}

.fill-b {{
    height: 100%;
    border-radius: inherit;
    background: linear-gradient(90deg, var(--purple), var(--pink));
    box-shadow: 0 0 15px rgba(244,114,182,.45);
    animation: bar 1s ease-out;
}}

/* ---------- Reason cards ---------- */

.reason-card {{
    height: 100%;
    padding: 1.4rem;
    border-radius: 22px;
    background: rgba(13,10,27,.72);
    border: 1px solid rgba(255,255,255,.09);
    box-shadow: 0 15px 45px rgba(0,0,0,.25);
}}

.reason-head {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
}}

.reason-title {{
    font-weight: 900;
    color: #fff;
}}

.reason-icon {{
    font-size: 1.4rem;
}}

.reason-text {{
    color: #b5aec1;
    line-height: 1.7;
    font-size: .88rem;
}}

.tag {{
    display: inline-flex;
    align-items: center;
    gap: .3rem;
    margin: .8rem .35rem 0 0;
    padding: .42rem .65rem;
    border-radius: 999px;
    color: #fda4af;
    background: rgba(251,113,133,.08);
    border: 1px solid rgba(251,113,133,.28);
    font-size: .68rem;
    font-weight: 900;
    letter-spacing: .04em;
}}

.clean {{
    display: inline-flex;
    align-items: center;
    gap: .35rem;
    margin-top: .9rem;
    color: #86efac;
    font-size: .75rem;
    font-weight: 800;
}}

/* ---------- Winner ---------- */

.winner {{
    position: relative;
    overflow: hidden;
    margin-top: 1.4rem;
    padding: 2.2rem 1.5rem;
    text-align: center;
    border-radius: 28px;
    background:
        radial-gradient(circle at 50% 0%, rgba(250,204,21,.15), transparent 50%),
        rgba(30,20,10,.72);
    border: 1px solid rgba(250,204,21,.35);
    box-shadow:
        0 25px 70px rgba(250,204,21,.10),
        inset 0 1px 0 rgba(255,255,255,.06);
    animation: winner .7s ease-out;
}}

.winner::before,
.winner::after {{
    content: "✦";
    position: absolute;
    color: #facc15;
    font-size: 1.4rem;
    animation: float 2.5s ease-in-out infinite;
}}

.winner::before {{ left: 12%; top: 25%; }}
.winner::after {{ right: 12%; top: 45%; animation-delay: -.8s; }}

.crown {{
    font-size: 3.2rem;
    display: block;
    animation: pulse 1.5s ease-in-out infinite;
}}

.winner-title {{
    margin-top: .5rem;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.8rem;
    font-weight: 900;
    color: #facc15;
    letter-spacing: .08em;
}}

.winner-reason {{
    max-width: 750px;
    margin: .65rem auto 0;
    color: #c9c0ce;
    line-height: 1.65;
    font-size: .88rem;
}}

/* ---------- Footer ---------- */

.footer {{
    text-align: center;
    color: #514b5d;
    font-size: .7rem;
    letter-spacing: .12em;
    text-transform: uppercase;
    margin-top: 3rem;
}}

@media (max-width: 700px) {{
    .main .block-container {{ padding: 1rem; }}
    .hero {{ padding-top: 1.5rem; }}
    .hero-title {{ font-size: 3.2rem; }}
    .vs-grid {{ grid-template-columns: 1fr; }}
    .vs {{ margin: 0 auto; }}
    .score-number {{ font-size: 2.8rem; }}
}}

</style>
"""

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# -------------------- Ambient HTML --------------------
st.markdown(
    """
    <div class="bg-layer"></div>
    <div class="aurora">
        <div class="orb one"></div>
        <div class="orb two"></div>
        <div class="orb three"></div>
    </div>
    <div class="grid"></div>
    """,
    unsafe_allow_html=True,
)

# -------------------- Intro screen --------------------
if "entered" not in st.session_state:
    st.session_state.entered = False

if not st.session_state.entered:
    st.markdown(
        """
        <div class="hero" style="padding-top:12vh;">
            <div class="hero-kicker">⚡ HACK TITANS · AI INNOVATION</div>
            <div class="hero-title">FALLACY<br>FINDER</div>
            <div class="hero-sub">🧠 AI Debate Intelligence Arena</div>
            <div class="hero-line"></div>
            <div style="color:#81798e;max-width:560px;margin:auto;line-height:1.7;">
                Detect weak reasoning. Expose logical fallacies.
                Compare arguments. Let AI deliver the verdict.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        if st.button("🚀  ENTER THE DEBATE ARENA", use_container_width=True):
            st.session_state.entered = True
            st.rerun()

    st.markdown(
        '<div class="footer">Built with 🧠 AI · ⚔️ Logic · 🏆 Competition</div>',
        unsafe_allow_html=True,
    )
    st.stop()

# -------------------- Main hero --------------------
st.markdown(
    """
    <div class="hero">
        <div class="hero-kicker">🔴 LIVE · AI REASONING ENGINE</div>
        <div class="hero-title" style="font-size:clamp(2.8rem,5vw,5rem);">
            🔍 FALLACY FINDER
        </div>
        <div class="hero-sub">AI-powered debate analysis · Tanglish + English</div>
        <div class="hero-line"></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------- Input area --------------------
st.markdown('<div class="section-label">📝 01 · BUILD YOUR DEBATE</div>', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="glass topic-card">', unsafe_allow_html=True)

    topic = st.text_input(
        "📝 DEBATE TOPIC",
        placeholder="Example: School la uniform kandippa venuma?",
    )

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown(
            '<div class="arg-header"><span class="arg-pill arg-a">🔵 ARGUMENT A</span><span style="color:#514b5d;font-size:.7rem;">SIDE A</span></div>',
            unsafe_allow_html=True,
        )
        argument_a = st.text_area(
            "Argument A",
            placeholder="Unga argument Tanglish or English la type pannunga...",
            height=170,
            label_visibility="collapsed",
        )

    with col2:
        st.markdown(
            '<div class="arg-header"><span class="arg-pill arg-b">🟣 ARGUMENT B</span><span style="color:#514b5d;font-size:.7rem;">SIDE B</span></div>',
            unsafe_allow_html=True,
        )
        argument_b = st.text_area(
            "Argument B",
            placeholder="Type your counter argument in Tanglish or English...",
            height=170,
            label_visibility="collapsed",
        )

    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    submitted = st.button("🚀  ANALYZE ARGUMENTS  ·  FIND FALLACIES", use_container_width=True)

# -------------------- Results --------------------
if submitted:
    if not topic.strip() or not argument_a.strip() or not argument_b.strip():
        st.warning("⚠️ Please fill in the topic and both arguments.")
        st.stop()

    search_box = st.empty()
    search_box.markdown(
        """
        <div class="scanner">
            <div class="scanner-icon">🧠</div>
            <div class="scanner-title">AI Reasoning Engine Active</div>
            <div class="scanner-sub">
                🔍 Scanning logic · 📚 checking evidence · ⚠️ detecting fallacies · 📊 calculating scores
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        result = judge_arguments(topic, argument_a, argument_b)
        time.sleep(.8)
    except Exception as e:
        search_box.empty()
        st.error(f"❌ AI analysis failed: {e}")
        st.stop()

    search_box.empty()

    a = result["argument_a"]
    b = result["argument_b"]

    total_a = a["logic"] + a["evidence"] + a["persuasiveness"]
    total_b = b["logic"] + b["evidence"] + b["persuasiveness"]

    winner = str(result["winner"]).strip().upper()
    winner_total = total_a if winner == "A" else total_b

    st.markdown('<div class="section-label">🧠 02 · AI ANALYSIS</div>', unsafe_allow_html=True)

    bars = ""
    metrics = [
        ("🧠 LOGIC", a["logic"], b["logic"]),
        ("📚 EVIDENCE", a["evidence"], b["evidence"]),
        ("💬 PERSUASIVENESS", a["persuasiveness"], b["persuasiveness"]),
    ]

    for label, va, vb in metrics:
        bars += f"""
        <div class="metric">
            <div class="metric-top">
                <span>{label}</span>
                <span class="metric-values">{va}/10&nbsp;&nbsp;&nbsp; {vb}/10</span>
            </div>
            <div class="metric-track">
                <div class="track"><div class="fill-a" style="width:{va*10}%"></div></div>
                <div class="track"><div class="fill-b" style="width:{vb*10}%"></div></div>
            </div>
        </div>
        """

    st.markdown(
        f"""
        <div class="glass scoreboard">
            <div class="vs-grid">
                <div class="score-side">
                    <div class="score-name">🔵 ARGUMENT A</div>
                    <div class="score-number">{total_a}</div>
                    <div class="score-max">TOTAL / 30</div>
                </div>

                <div class="vs">VS</div>

                <div class="score-side">
                    <div class="score-name">🟣 ARGUMENT B</div>
                    <div class="score-number">{total_b}</div>
                    <div class="score-max">TOTAL / 30</div>
                </div>
            </div>
            {bars}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-label">⚠️ 03 · FALLACY DETECTION</div>', unsafe_allow_html=True)

    def safe_text(value):
        return html.escape(str(value))

    def fallacy_tags(items):
        if items:
            return "".join(
                f'<span class="tag">⚠️ {safe_text(item)}</span>'
                for item in items
            )
        return '<div class="clean">✨ No fallacies detected</div>'

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown(
            f"""
            <div class="reason-card">
                <div class="reason-head">
                    <div class="reason-title">🔵 Argument A</div>
                    <div class="reason-icon">🧠</div>
                </div>
                <div class="reason-text">{safe_text(a["reason"])}</div>
                {fallacy_tags(a["fallacies"])}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="reason-card">
                <div class="reason-head">
                    <div class="reason-title">🟣 Argument B</div>
                    <div class="reason-icon">🧠</div>
                </div>
                <div class="reason-text">{safe_text(b["reason"])}</div>
                {fallacy_tags(b["fallacies"])}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-label">👑 04 · FINAL VERDICT</div>', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="winner">
            <span class="crown">👑</span>
            <div class="winner-title">🏆 ARGUMENT {safe_text(winner)} WINS</div>
            <div style="color:#facc15;font-weight:900;margin-top:.35rem;">
                {winner_total} / 30 · STRONGER REASONING
            </div>
            <div class="winner-reason">{safe_text(result["overall_reason"])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="footer">🔍 FALLACY FINDER · HACK TITANS · AI DEBATE INTELLIGENCE</div>',
        unsafe_allow_html=True,
    )


