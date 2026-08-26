import streamlit as st
import google.generativeai as genai
import os
import json
import time
import base64
import html

# =========================================================
# FALLACY FINDER — HACK TITANS
# Premium cinematic Streamlit UI
# =========================================================

st.set_page_config(
    page_title="Fallacy Finder | Hack Titans",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------- AI ----------------

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-3.6-flash")


def judge_arguments(topic, argument_a, argument_b):
    prompt = f"""
You are an impartial debate judge and logical fallacy expert.

The topic and arguments may be written in Tanglish (Tamil written in English/Roman
letters, often mixed with English). Understand Tanglish naturally.

Topic:
{topic}

Argument A:
{argument_a}

Argument B:
{argument_b}

Judge only the reasoning and evidence in the text itself.

Score both arguments from 0-10 for:
1. logic
2. evidence
3. persuasiveness

Also identify logical fallacies in each argument.
If there are none, return an empty list.

Write reason and overall_reason in simple Tanglish.
Keep fallacy names in English.

Return ONLY valid JSON:

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

    response = model.generate_content(prompt)
    raw = response.text.strip()

    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"):
            raw = raw[4:]

    return json.loads(raw)


# ---------------- Background image ----------------

@st.cache_data
def load_background():
    path = "assets/background.jpg"
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return ""


BG = load_background()

background_rule = (
    f'background-image:linear-gradient(rgba(4,3,12,.55),rgba(4,3,12,.88)),'
    f'url("data:image/jpg;base64,{BG}");'
    if BG
    else ""
)


# ---------------- Premium CSS ----------------

CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Space+Grotesk:wght@500;600;700&display=swap');

:root{
    --bg:#04030b;
    --panel:rgba(10,8,23,.74);
    --panel2:rgba(17,11,34,.82);
    --purple:#9b5cff;
    --pink:#f45bb8;
    --cyan:#36d9ff;
    --gold:#ffd75a;
    --green:#4ade80;
    --text:#f8fafc;
    --muted:#8e889d;
}

*{box-sizing:border-box}
html,body,[class*="css"]{font-family:Inter,sans-serif}
.stApp{
    min-height:100vh;
    background:
        radial-gradient(circle at 18% 12%,rgba(155,92,255,.16),transparent 28%),
        radial-gradient(circle at 84% 28%,rgba(54,217,255,.10),transparent 25%),
        radial-gradient(circle at 50% 100%,rgba(244,91,184,.10),transparent 32%),
        var(--bg);
    color:var(--text);
}
header[data-testid="stHeader"]{background:transparent!important}
footer{visibility:hidden}
#MainMenu{visibility:hidden}
.main .block-container{max-width:1250px;padding:1.5rem 1.5rem 4rem}

body:before{
    content:"";
    position:fixed;inset:0;pointer-events:none;z-index:40;
    background:
      repeating-linear-gradient(0deg,rgba(255,255,255,.035) 0 1px,transparent 1px 5px);
    opacity:.11;
}
body:after{
    content:"";
    position:fixed;inset:0;pointer-events:none;z-index:41;
    background:
      radial-gradient(circle at 20% 30%,rgba(255,255,255,.22) 0 1px,transparent 2px),
      radial-gradient(circle at 70% 18%,rgba(255,255,255,.18) 0 1px,transparent 2px),
      radial-gradient(circle at 82% 75%,rgba(255,255,255,.15) 0 1px,transparent 2px);
    background-size:170px 170px,230px 230px,280px 280px;
    opacity:.13;
    animation:stars 22s linear infinite;
}
@keyframes stars{
    from{transform:translate(0,0)}
    to{transform:translate(-35px,25px)}
}

.bg{
    position:fixed;inset:-6%;z-index:-10;
    background-size:cover;background-position:center;
    __BACKGROUND__;
    filter:saturate(1.12);
    animation:bgMove 24s ease-in-out infinite alternate;
}
@keyframes bgMove{
    from{transform:scale(1)}
    to{transform:scale(1.08) translate(-1%,-1%)}
}

.aurora{
    position:fixed;inset:0;z-index:-9;pointer-events:none;overflow:hidden;
}
.aurora span{
    position:absolute;border-radius:50%;filter:blur(90px);opacity:.18;
    animation:orb 15s ease-in-out infinite alternate;
}
.a1{width:420px;height:420px;background:#8b5cf6;left:-100px;top:5%}
.a2{width:350px;height:350px;background:#22d3ee;right:-80px;top:20%;animation-delay:-5s!important}
.a3{width:360px;height:360px;background:#ec4899;left:40%;bottom:-180px;animation-delay:-9s!important}
@keyframes orb{
    from{transform:translate(0,0) scale(.9)}
    to{transform:translate(60px,-40px) scale(1.14)}
}

/* ---------- intro ---------- */

.intro{
    min-height:78vh;
    position:relative;
    overflow:hidden;
    display:flex;
    align-items:center;
    justify-content:center;
    padding:2rem;
    border-radius:34px;
    background:
      radial-gradient(circle at 50% 34%,rgba(155,92,255,.22),transparent 32%),
      linear-gradient(160deg,rgba(15,9,32,.94),rgba(3,2,9,.82));
    border:1px solid rgba(255,255,255,.10);
    box-shadow:0 45px 120px rgba(0,0,0,.48),inset 0 1px 0 rgba(255,255,255,.06);
}
.intro:before{
    content:"";
    position:absolute;inset:20px;border-radius:26px;
    border:1px solid rgba(155,92,255,.22);
    pointer-events:none;
}
.intro:after{
    content:"";
    position:absolute;inset:0;pointer-events:none;
    background:
      linear-gradient(90deg,transparent 49.5%,rgba(155,92,255,.05) 50%,transparent 50.5%),
      linear-gradient(transparent 49.5%,rgba(54,217,255,.04) 50%,transparent 50.5%);
    background-size:84px 84px;
    mask-image:radial-gradient(circle at center,#000 0%,transparent 78%);
}
.intro-content{position:relative;z-index:2;text-align:center;max-width:900px;width:100%}
.pill{
    display:inline-flex;gap:.55rem;align-items:center;
    padding:.55rem .95rem;border-radius:999px;
    background:rgba(155,92,255,.08);
    border:1px solid rgba(155,92,255,.30);
    color:#dfccff;font-size:.68rem;font-weight:900;letter-spacing:.18em;
    text-transform:uppercase;
    animation:rise .8s both;
}
.team{
    margin-top:1.2rem;font-family:'Space Grotesk',sans-serif;
    color:#fff;font-size:1rem;font-weight:900;letter-spacing:.42em;
    padding-left:.42em;
    text-shadow:0 0 30px rgba(155,92,255,.5);
    animation:rise .9s .08s both;
}
.title{
    margin:.9rem 0 .55rem;
    font-family:'Space Grotesk',sans-serif;
    font-size:clamp(4rem,10vw,8rem);
    line-height:.84;font-weight:900;letter-spacing:-.07em;
    background:linear-gradient(110deg,#fff,#d8b4fe,#f472b6,#60e5ff,#fff);
    background-size:250% auto;
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    animation:rise 1s .16s both,shine 6s linear infinite;
}
@keyframes shine{to{background-position:250%}}
.subtitle{
    color:#b4adc0;font-size:.78rem;font-weight:800;
    letter-spacing:.24em;text-transform:uppercase;
    animation:rise 1s .24s both;
}
.desc{
    max-width:620px;margin:1rem auto 0;color:#777083;
    font-size:.88rem;line-height:1.75;animation:rise 1s .32s both;
}
@keyframes rise{
    from{opacity:0;transform:translateY(24px) scale(.98)}
    to{opacity:1;transform:none}
}
.glow-line{
    width:230px;height:2px;margin:1.4rem auto;
    background:linear-gradient(90deg,transparent,#9b5cff,#36d9ff,transparent);
    box-shadow:0 0 22px rgba(155,92,255,.7);
    animation:pulse 2.5s infinite;
}
@keyframes pulse{0%,100%{opacity:.45;transform:scaleX(.8)}50%{opacity:1;transform:scaleX(1)}}

.feature-row{
    display:flex;justify-content:center;gap:.7rem;flex-wrap:wrap;margin:1.35rem 0 1.7rem;
    animation:rise 1s .4s both;
}
.feature{
    min-width:130px;padding:.75rem .9rem;border-radius:16px;
    background:rgba(255,255,255,.025);
    border:1px solid rgba(255,255,255,.08);
}
.feature b{display:block;font-size:.85rem;color:#fff}
.feature span{display:block;margin-top:.18rem;color:#676071;font-size:.58rem;letter-spacing:.12em;text-transform:uppercase}
.spark{
    position:absolute;color:#fff;opacity:.5;font-size:.8rem;z-index:2;
    animation:float 3.5s ease-in-out infinite;
}
.s1{left:13%;top:25%}.s2{right:15%;top:27%;animation-delay:-1s}.s3{left:18%;bottom:21%;animation-delay:-2s}.s4{right:17%;bottom:24%;animation-delay:-.4s}
@keyframes float{50%{transform:translateY(-16px) rotate(8deg);opacity:.9}}


.title span{
    background:linear-gradient(100deg,#f472b6,#a855f7,#22d3ee,#ffffff,#f472b6);
    background-size:250% auto;
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}

/* ---------- main ---------- */

.brandbar{
    width:max-content;margin:.25rem auto 1.1rem;
    padding:.52rem .9rem;border-radius:999px;
    border:1px solid rgba(255,255,255,.08);
    background:rgba(7,5,17,.62);
    box-shadow:0 0 35px rgba(155,92,255,.10);
    display:flex;align-items:center;gap:.55rem;
}
.brandbar i{
    width:7px;height:7px;border-radius:50%;
    background:#4ade80;box-shadow:0 0 12px rgba(74,222,128,.8)
}
.brandbar b{
    font-family:'Space Grotesk',sans-serif;letter-spacing:.28em;
    padding-left:.28em;font-size:.74rem;
}
.brandbar small{color:#5f586b;letter-spacing:.12em}

.main-title{
    text-align:center;font-family:'Space Grotesk',sans-serif;
    font-size:clamp(2.7rem,5vw,4.8rem);font-weight:900;line-height:.95;
    letter-spacing:-.05em;
    background:linear-gradient(110deg,#fff,#d8b4fe,#f472b6,#67e8f9);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
}
.main-sub{text-align:center;color:#777083;margin:.6rem auto 1.5rem;font-size:.82rem;letter-spacing:.15em;text-transform:uppercase}

.card{
    position:relative;padding:1.45rem;border-radius:26px;
    background:
      radial-gradient(circle at 15% 0%,rgba(155,92,255,.07),transparent 24%),
      rgba(9,7,20,.72);
    border:1px solid rgba(255,255,255,.09);
    box-shadow:0 25px 75px rgba(0,0,0,.34),inset 0 1px 0 rgba(255,255,255,.05);
    backdrop-filter:blur(18px);
}
.section{
    color:#c9b6e9;font-weight:900;font-size:.68rem;
    letter-spacing:.19em;text-transform:uppercase;
    margin:1.2rem 0 .75rem;
}
.stTextInput>div>div,.stTextArea>div>div{
    background:rgba(255,255,255,.025)!important;
    border:1px solid rgba(255,255,255,.09)!important;
    border-radius:15px!important;
}
.stTextInput>div>div:focus-within,.stTextArea>div>div:focus-within{
    border-color:rgba(155,92,255,.75)!important;
    box-shadow:0 0 0 3px rgba(155,92,255,.10),0 0 28px rgba(155,92,255,.12)!important;
}
.stTextInput input,.stTextArea textarea{color:#fff!important;background:transparent!important}
.stTextInput input::placeholder,.stTextArea textarea::placeholder{color:#5f5968!important}
label[data-testid="stWidgetLabel"] p{color:#c4b5fd!important;font-weight:800!important;font-size:.74rem!important}

.argtag{
    display:inline-flex;align-items:center;gap:.45rem;
    border-radius:999px;padding:.43rem .7rem;font-size:.68rem;font-weight:900;
    letter-spacing:.08em;margin-bottom:.55rem;
}
.a{color:#67e8f9;border:1px solid rgba(54,217,255,.28);background:rgba(54,217,255,.07)}
.b{color:#e9b9ff;border:1px solid rgba(155,92,255,.30);background:rgba(155,92,255,.08)}

.stButton>button,.stFormSubmitButton>button{
    width:100%;min-height:54px;border:0!important;border-radius:16px!important;
    color:#fff!important;font-weight:900!important;letter-spacing:.06em;
    background:linear-gradient(100deg,#6633d7,#9b5cff,#f45bb8,#6633d7)!important;
    background-size:250% 100%!important;
    box-shadow:0 14px 40px rgba(155,92,255,.28),inset 0 1px 0 rgba(255,255,255,.20);
    transition:.25s!important;
}
.stButton>button:hover,.stFormSubmitButton>button:hover{
    transform:translateY(-3px);background-position:100% 0!important;
    box-shadow:0 18px 48px rgba(155,92,255,.40);
}

.scan{
    position:relative;overflow:hidden;text-align:center;margin:1.6rem 0;
    padding:2.4rem 1rem;border-radius:25px;background:rgba(6,5,14,.82);
    border:1px solid rgba(155,92,255,.22);
}
.scan:after{
    content:"";position:absolute;left:8%;right:8%;top:0;height:2px;
    background:linear-gradient(90deg,transparent,#36d9ff,#9b5cff,#f45bb8,transparent);
    box-shadow:0 0 20px rgba(54,217,255,.8);animation:scan 2.2s ease-in-out infinite;
}
@keyframes scan{0%{transform:translateY(-120px);opacity:0}20%,80%{opacity:1}100%{transform:translateY(220px);opacity:0}}
.scan-icon{font-size:3rem;animation:scanIcon 1.3s ease-in-out infinite}
@keyframes scanIcon{50%{transform:scale(1.12);filter:drop-shadow(0 0 18px rgba(155,92,255,.65))}}
.scan b{display:block;margin-top:.4rem;letter-spacing:.16em;font-size:.74rem}
.scan small{color:#6c6574;font-size:.72rem}

.result{
    padding:1.6rem;border-radius:28px;background:
      radial-gradient(circle at 50% 0%,rgba(155,92,255,.11),transparent 40%),
      rgba(7,5,17,.78);
    border:1px solid rgba(255,255,255,.09);
    box-shadow:0 28px 90px rgba(0,0,0,.42);
}
.scores{
    display:grid;grid-template-columns:1fr auto 1fr;gap:1rem;align-items:center;text-align:center
}
.score-name{color:#c8bfda;font-weight:900;font-size:.76rem;letter-spacing:.12em}
.score{
    font-family:'Space Grotesk',sans-serif;font-size:3.25rem;font-weight:900;
    margin:.2rem 0;background:linear-gradient(120deg,#fff,#d8b4fe,#f45bb8);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
}
.vs{
    width:50px;height:50px;border-radius:50%;display:grid;place-items:center;
    border:1px solid rgba(255,215,90,.32);color:#ffd75a;font-weight:900;
    background:rgba(255,215,90,.06);box-shadow:0 0 25px rgba(255,215,90,.12)
}
.metric{margin-top:1rem}
.metric-top{display:flex;justify-content:space-between;color:#82798d;font-size:.7rem;font-weight:800}
.trackrow{display:grid;grid-template-columns:1fr 1fr;gap:5px;margin-top:.35rem}
.track{height:9px;background:rgba(255,255,255,.06);border-radius:999px;overflow:hidden}
.fillA{height:100%;background:linear-gradient(90deg,#36d9ff,#9b5cff);border-radius:inherit;animation:bar 1s both}
.fillB{height:100%;background:linear-gradient(90deg,#9b5cff,#f45bb8);border-radius:inherit;animation:bar 1s both}
@keyframes bar{from{width:0}}

.reason{
    height:100%;padding:1.25rem;border-radius:21px;
    background:rgba(10,8,22,.72);border:1px solid rgba(255,255,255,.08);
}
.reason h3{font-size:.9rem;margin:0 0 .8rem}
.reason p{color:#aaa2b5!important;text-align:left!important;line-height:1.7;font-size:.82rem}
.tag{display:inline-block;margin:.35rem .25rem 0 0;padding:.4rem .6rem;border-radius:999px;
    color:#fda4af;background:rgba(244,91,119,.07);border:1px solid rgba(244,91,119,.25);
    font-size:.65rem;font-weight:900}

.winner{
    position:relative;overflow:hidden;margin-top:1.4rem;padding:2.8rem 1.4rem 2.2rem;
    text-align:center;border-radius:32px;
    background:
      radial-gradient(circle at 50% 15%,rgba(255,215,90,.23),transparent 35%),
      radial-gradient(circle at 50% 100%,rgba(155,92,255,.10),transparent 45%),
      rgba(29,20,9,.88);
    border:1px solid rgba(255,215,90,.42);
    box-shadow:0 25px 85px rgba(255,215,90,.12),inset 0 1px 0 rgba(255,255,255,.06);
    animation:winnerIn .85s cubic-bezier(.2,.8,.2,1);
}
@keyframes winnerIn{from{opacity:0;transform:translateY(30px) scale(.9)}to{opacity:1;transform:none}}
.winner:before{
    content:"✦  ✧  ✦  ✧  ✦";
    position:absolute;top:12px;left:0;right:0;color:rgba(255,215,90,.45);
    font-size:.65rem;letter-spacing:1.05rem;
}
.crown{font-size:4rem;display:block;filter:drop-shadow(0 0 18px rgba(255,215,90,.55));animation:crown 2s ease-in-out infinite}
@keyframes crown{50%{transform:translateY(-9px) rotate(2deg)}}
.winner h2{margin:.45rem 0 0;font-family:'Space Grotesk',sans-serif;font-size:2rem;color:#ffd75a}
.winner .pill2{display:inline-block;margin:.65rem 0;padding:.45rem .8rem;border-radius:999px;
    color:#fff4c2;background:rgba(255,215,90,.08);border:1px solid rgba(255,215,90,.24);font-size:.68rem;font-weight:900}
.winner p{max-width:760px;margin:0 auto;color:#bcb4c0!important;text-align:center!important;line-height:1.7}

@media(max-width:700px){
    .main .block-container{padding:1rem}
    .scores{grid-template-columns:1fr}
    .vs{margin:auto}
    .intro{min-height:75vh;padding:1.2rem}
}
</style>
"""

CSS = CSS.replace("__BACKGROUND__", background_rule)
st.markdown(CSS, unsafe_allow_html=True)

st.markdown(
    """
    <div class="bg"></div>
    <div class="aurora">
        <span class="a1"></span>
        <span class="a2"></span>
        <span class="a3"></span>
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# INTRO
# =========================================================

if "entered" not in st.session_state:
    st.session_state.entered = False

if not st.session_state.entered:
    st.markdown(
        """
        <div class="intro">
            <div class="spark s1">✦</div>
            <div class="spark s2">◇</div>
            <div class="spark s3">✧</div>
            <div class="spark s4">⚡</div>

            <div class="intro-content">
                <div class="pill">⚡ HACK TITANS · AI DEBATE ARENA</div>

                <div class="team">HACK TITANS</div>

                <div class="title">
                    FALLACY<br>
                    <span>FINDER</span>
                </div>

                <div class="subtitle">
                    🧠 AI-POWERED LOGIC INTELLIGENCE
                </div>

                <div class="glow-line"></div>

                <div class="desc">
                    Discover weak reasoning, expose hidden logical fallacies,
                    compare two arguments and let AI choose the stronger case.
                </div>

                <div class="feature-row">
                    <div class="feature">
                        <b>🧠 AI JUDGE</b>
                        <span>Smart Analysis</span>
                    </div>

                    <div class="feature">
                        <b>⚠️ FALLACY SCAN</b>
                        <span>Logic Detection</span>
                    </div>

                    <div class="feature">
                        <b>🏆 AI VERDICT</b>
                        <span>Fair Decision</span>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


    st.write("")
    left, middle, right = st.columns([1, 1.4, 1])
    with middle:
        if st.button(
            "🚀  ENTER THE DEBATE ARENA",
            use_container_width=True,
            key="intro_enter",
        ):
            st.session_state.entered = True
            st.rerun()

    st.markdown(
        '<div style="text-align:center;color:#555061;font-size:.62rem;letter-spacing:.15em;text-transform:uppercase;margin-top:1.2rem;">Tanglish + English supported</div>',
        unsafe_allow_html=True,
    )
    st.stop()


# =========================================================
# MAIN APP
# =========================================================

st.markdown(
    """
    <div class="brandbar">
        <i></i>
        <b>HACK TITANS</b>
        <small>AI DEBATE LAB</small>
    </div>
    <div class="main-title">🔍 FALLACY FINDER</div>
    <div class="main-sub">AI-powered debate intelligence</div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section">📝 Create your debate</div>', unsafe_allow_html=True)

topic = st.text_input(
    "Debate Topic",
    placeholder="Example: School la uniform kandippa venuma?",
    key="topic_input",
)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown('<div class="argtag a">🔵 SIDE A</div>', unsafe_allow_html=True)
    argument_a = st.text_area(
        "Argument A",
        placeholder="Unga argument Tanglish or English la type pannunga...",
        height=170,
        label_visibility="collapsed",
        key="argument_a_input",
    )

with col2:
    st.markdown('<div class="argtag b">🟣 SIDE B</div>', unsafe_allow_html=True)
    argument_b = st.text_area(
        "Argument B",
        placeholder="Counter argument Tanglish or English la type pannunga...",
        height=170,
        label_visibility="collapsed",
        key="argument_b_input",
    )

st.write("")
submitted = st.button(
    "🚀  ANALYZE ARGUMENTS",
    use_container_width=True,
    key="analyze_button",
)

if submitted:
    if not topic.strip() or not argument_a.strip() or not argument_b.strip():
        st.warning("⚠️ Please enter the topic and both arguments.")
        st.stop()

    scan = st.empty()
    scan.markdown(
        """
        <div class="scan">
            <div class="scan-icon">🧠</div>
            <b>AI IS ANALYZING</b>
            <small>🔍 Logic · 📚 Evidence · ⚠️ Fallacies · 🏆 Verdict</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        result = judge_arguments(topic, argument_a, argument_b)
        time.sleep(.8)
    except Exception as exc:
        scan.empty()
        st.error(f"Analysis failed: {exc}")
        st.stop()

    scan.empty()

    a = result["argument_a"]
    b = result["argument_b"]

    total_a = a["logic"] + a["evidence"] + a["persuasiveness"]
    total_b = b["logic"] + b["evidence"] + b["persuasiveness"]

    winner = str(result["winner"]).strip().upper()
    winner_total = total_a if winner == "A" else total_b

    def clean(v):
        return html.escape(str(v))

    def tags(items):
        if not items:
            return '<span style="color:#4ade80;font-size:.72rem;font-weight:800;">✨ No fallacies detected</span>'
        return "".join(f'<span class="tag">⚠️ {clean(x)}</span>' for x in items)

    metrics = [
        ("🧠 LOGIC", a["logic"], b["logic"]),
        ("📚 EVIDENCE", a["evidence"], b["evidence"]),
        ("💬 PERSUASIVENESS", a["persuasiveness"], b["persuasiveness"]),
    ]

    metric_html = ""
    for label, va, vb in metrics:
        metric_html += f"""
        <div class="metric">
            <div class="metric-top"><span>{label}</span><span>{va}/10 &nbsp;&nbsp; {vb}/10</span></div>
            <div class="trackrow">
                <div class="track"><div class="fillA" style="width:{va*10}%"></div></div>
                <div class="track"><div class="fillB" style="width:{vb*10}%"></div></div>
            </div>
        </div>
        """

    st.markdown('<div class="section">🧠 AI verdict</div>', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="result">
            <div class="scores">
                <div>
                    <div class="score-name">🔵 SIDE A</div>
                    <div class="score">{total_a}</div>
                    <div style="color:#5f5868;font-size:.62rem;letter-spacing:.12em;">OUT OF 30</div>
                </div>
                <div class="vs">VS</div>
                <div>
                    <div class="score-name">🟣 SIDE B</div>
                    <div class="score">{total_b}</div>
                    <div style="color:#5f5868;font-size:.62rem;letter-spacing:.12em;">OUT OF 30</div>
                </div>
            </div>
            {metric_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section">⚠️ Fallacy detection</div>', unsafe_allow_html=True)

    ca, cb = st.columns(2, gap="large")

    with ca:
        st.markdown(
            f"""
            <div class="reason">
                <h3>🔵 Side A</h3>
                <p>{clean(a["reason"])}</p>
                {tags(a["fallacies"])}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with cb:
        st.markdown(
            f"""
            <div class="reason">
                <h3>🟣 Side B</h3>
                <p>{clean(b["reason"])}</p>
                {tags(b["fallacies"])}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section">👑 Final decision</div>', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="winner">
            <span class="crown">👑</span>
            <h2>🏆 SIDE {clean(winner)} WINS</h2>
            <div class="pill2">⚡ {winner_total} / 30 · STRONGER ARGUMENT</div>
            <p>{clean(result["overall_reason"])}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    if st.button("🔄  DEBATE ANOTHER TOPIC", use_container_width=True, key="reset_debate"):
        for key in ["topic_input", "argument_a_input", "argument_b_input"]:
            st.session_state.pop(key, None)
        st.rerun()

st.markdown(
    '<div style="text-align:center;color:#4e4857;font-size:.62rem;letter-spacing:.15em;text-transform:uppercase;margin-top:2.2rem;">HACK TITANS · FALLACY FINDER</div>',
    unsafe_allow_html=True,
)
