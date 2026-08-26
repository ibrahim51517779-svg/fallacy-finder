import streamlit as st
import google.generativeai as genai
import os
import json
import pandas as pd
import time

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-3.6-flash")


def judge_arguments(topic, argument_a, argument_b):
    prompt = (
        "You are an impartial debate judge and logical fallacy expert.\n\n"
        f"Topic: {topic}\n\n"
        f"Argument A: {argument_a}\n\n"
        f"Argument B: {argument_b}\n\n"
        "Judge only the strength of reasoning and evidence in the text itself. "
        "Do not favor either side based on argument length, order, or writing style alone.\n\n"
        "Evaluate both arguments on: logic, evidence, and persuasiveness (each scored 0-10). "
        "Also identify any logical fallacies present in each argument. If none are present, return an empty list.\n\n"
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


# ---------- PAGE SETUP ----------
st.set_page_config(page_title="Fallacy Finder", page_icon="✨", layout="centered")

PAGE_STYLE = """
<style>
@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
@keyframes glowPulse {
    0%, 100% { text-shadow: 0 0 20px rgba(244,114,182,0.8), 0 0 40px rgba(168,85,247,0.5); }
    50% { text-shadow: 0 0 30px rgba(250,204,21,0.9), 0 0 60px rgba(244,114,182,0.6); }
}
@keyframes floatUp {
    0% { transform: translateY(0); opacity: 0; }
    10% { opacity: 1; }
    90% { opacity: 1; }
    100% { transform: translateY(-100vh); opacity: 0; }
}
@keyframes popIn {
    0% { opacity: 0; transform: scale(0.7) translateY(30px); }
    60% { opacity: 1; transform: scale(1.05) translateY(-5px); }
    100% { opacity: 1; transform: scale(1) translateY(0); }
}
.stApp {
    background: linear-gradient(-45deg, #1a0b2e, #2d1b4e, #3b0764, #1a0b2e);
    background-size: 400% 400%;
    animation: gradientShift 12s ease infinite;
}
.sparkle {
    position: fixed;
    font-size: 1.3em;
    animation: floatUp linear infinite;
    pointer-events: none;
    z-index: 0;
}
.team-banner {
    text-align: center;
    font-size: 2.6em;
    font-weight: 900;
    letter-spacing: 10px;
    background: linear-gradient(90deg, #f472b6, #facc15, #a855f7, #f472b6);
    background-size: 300% 300%;
    animation: gradientShift 6s ease infinite, glowPulse 3s ease-in-out infinite;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0;
    position: relative;
    z-index: 1;
}
.team-sub {
    text-align: center;
    color: #e9d5ff;
    font-size: 0.85em;
    letter-spacing: 5px;
    margin-bottom: 1.3em;
    opacity: 0.85;
    position: relative;
    z-index: 1;
}
h1 {
    text-align: center;
    background: linear-gradient(90deg, #f472b6, #a855f7, #facc15);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    font-size: 2.8em !important;
    position: relative;
    z-index: 1;
}
.stCaption, p {
    text-align: center;
    color: #e9d5ff !important;
}
div[data-testid="stForm"] {
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 22px;
    padding: 2em;
    box-shadow: 0 8px 40px rgba(168,85,247,0.25);
    position: relative;
    z-index: 1;
}
.stTextArea textarea, .stTextInput input {
    background: rgba(255,255,255,0.08) !important;
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    color: white !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border: 1px solid #f472b6 !important;
    box-shadow: 0 0 18px rgba(244,114,182,0.6) !important;
}
.stButton>button {
    width: 100%;
    border-radius: 14px;
    height: 3.3em;
    font-weight: 700;
    font-size: 1.05em;
    background: linear-gradient(90deg, #f472b6, #a855f7, #facc15);
    background-size: 200% 200%;
    color: white;
    border: none;
    transition: 0.3s;
    box-shadow: 0 4px 25px rgba(168,85,247,0.5);
}
.stButton>button:hover {
    background-position: 100% 0;
    transform: scale(1.02);
}
.score-section {
    animation: popIn 0.6s ease-out;
    position: relative;
    z-index: 1;
}
.winner-box {
    text-align: center;
    background: rgba(250,204,21,0.1);
    border: 1px solid rgba(250,204,21,0.5);
    border-radius: 20px;
    padding: 1.4em;
    margin-top: 1em;
    box-shadow: 0 8px 35px rgba(250,204,21,0.25);
    animation: popIn 0.7s ease-out;
    position: relative;
    z-index: 1;
}
.winner-title {
    font-size: 1.6em;
    font-weight: 800;
    background: linear-gradient(90deg, #facc15, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 2px;
}
</style>

<div class="sparkle" style="left:8%; animation-duration:9s; animation-delay:0s;">&#10024;</div>
<div class="sparkle" style="left:22%; animation-duration:11s; animation-delay:2s;">&#11088;</div>
<div class="sparkle" style="left:38%; animation-duration:8s; animation-delay:1s;">&#10024;</div>
<div class="sparkle" style="left:54%; animation-duration:12s; animation-delay:3s;">&#128171;</div>
<div class="sparkle" style="left:70%; animation-duration:10s; animation-delay:0.5s;">&#10024;</div>
<div class="sparkle" style="left:86%; animation-duration:9s; animation-delay:2.5s;">&#11088;</div>
<div class="sparkle" style="left:15%; animation-duration:13s; animation-delay:4s;">&#128171;</div>
<div class="sparkle" style="left:94%; animation-duration:8s; animation-delay:1.5s;">&#10024;</div>
"""

st.markdown(PAGE_STYLE, unsafe_allow_html=True)

st.markdown('<div class="team-banner">HACK TITANS</div>', unsafe_allow_html=True)
st.markdown('<div class="team-sub">PRESENTS</div>', unsafe_allow_html=True)
st.title("✨ Fallacy Finder")
st.caption("Spot weak logic and score arguments fairly, powered by AI.")

# ---------- INPUT FORM ----------
with st.form("judge_form"):
    topic = st.text_input("Debate Topic", placeholder="e.g. Should social media have a minimum age?")
    col1, col2 = st.columns(2)
    with col1:
        argument_a = st.text_area("Argument A", height=150)
    with col2:
        argument_b = st.text_area("Argument B", height=150)
    submitted = st.form_submit_button("🔍 Find the Fallacies")

# ---------- RUN + DISPLAY ----------
if submitted:
    if not topic or not argument_a or not argument_b:
        st.warning("Please fill in the topic and both arguments.")
    else:
        search_box = st.empty()
        search_box.markdown(
            '<div style="text-align:center; padding:2em;">'
            '<div style="font-size:3.5em;">🔍</div>'
            '<div style="color:#e9d5ff; letter-spacing:2px; margin-top:0.5em;">'
            'Scanning arguments for logical fallacies...</div></div>',
            unsafe_allow_html=True,
        )

        result = judge_arguments(topic, argument_a, argument_b)
        time.sleep(1.5)
        search_box.empty()

        a = result["argument_a"]
        b = result["argument_b"]
        total_a = a["logic"] + a["evidence"] + a["persuasiveness"]
        total_b = b["logic"] + b["evidence"] + b["persuasiveness"]

        st.markdown('<div class="score-section">', unsafe_allow_html=True)
        st.divider()
        st.subheader("📊 Scoreboard")

        score_table = pd.DataFrame({
            "Criterion": ["Logic", "Evidence", "Persuasiveness", "TOTAL"],
            "Argument A": [a["logic"], a["evidence"], a["persuasiveness"], total_a],
            "Argument B": [b["logic"], b["evidence"], b["persuasiveness"], total_b],
        })
        st.table(score_table.set_index("Criterion"))

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Argument A reasoning:**")
            st.info(a["reason"])
            if a["fallacies"]:
                st.error("⚠️ Fallacies: " + ", ".join(a["fallacies"]))
            else:
                st.success("✅ No fallacies detected")
        with col2:
            st.markdown("**Argument B reasoning:**")
            st.info(b["reason"])
            if b["fallacies"]:
                st.error("⚠️ Fallacies: " + ", ".join(b["fallacies"]))
            else:
                st.success("✅ No fallacies detected")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            '<div class="winner-box">'
            f'<div class="winner-title">🏆 Winner: Argument {result["winner"]}</div>'
            f'<div style="color:#e9d5ff; margin-top:0.5em;">{result["overall_reason"]}</div>'
            '</div>',
            unsafe_allow_html=True,
        )