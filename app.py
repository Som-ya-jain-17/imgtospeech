import streamlit as st
import azure.cognitiveservices.speech as speechsdk
import tempfile

# =========================
# AZURE CONFIG (YOUR KEYS)
# =========================
SPEECH_KEY = "2LNcNfQUrK6f0jj3eZ1ssHm1qALaeiXmn1foajdEdGGo9bxH06i5JQQJ99CEACYeBjFXJ3w3AAAYACOGrjDr"
SPEECH_REGION = "eastus"

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="AI Text → Speech Studio",
    layout="wide",
    page_icon="🎧"
)

# =========================
# 🌌 PREMIUM DARK UI
# =========================
st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #05060a, #0a0f1a, #05060a);
    color: white;
}

/* TITLE */
.title {
    text-align:center;
    font-size: 50px;
    font-weight: 900;
    background: linear-gradient(90deg,#8b5cf6,#06b6d4,#ff2d95);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* SUBTITLE */
.subtitle {
    text-align:center;
    color:#aaa;
    margin-bottom:30px;
}

/* CARD */
.card {
    background: rgba(255,255,255,0.04);
    border-radius: 20px;
    padding: 30px;
    backdrop-filter: blur(20px);
    border: 1px solid rgba(139,92,246,0.3);
    box-shadow: 0 0 40px rgba(6,182,212,0.2);
}

/* BUTTON */
.stButton>button {
    background: linear-gradient(90deg,#8b5cf6,#06b6d4,#ff2d95);
    color: white;
    border-radius: 12px;
    padding: 12px 20px;
    border: none;
    font-weight: bold;
    transition: 0.3s;
}

.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 25px rgba(255,45,149,0.6);
}

/* TEXT AREA */
textarea {
    background-color: #0b0f1a !important;
    color: white !important;
    border-radius: 10px !important;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background-color: #06090f;
}

</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.markdown('<div class="title">🎧 AI Text → Speech Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Generate Natural Voice using Azure AI</div>', unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================
st.sidebar.header("⚙️ Settings")

voice = st.sidebar.selectbox(
    "🎤 Select Voice",
    [
        "en-US-JennyNeural",
        "en-IN-NeerjaNeural",
        "en-GB-RyanNeural"
    ]
)

# =========================
# FUNCTION
# =========================
def text_to_speech(text):
    speech_config = speechsdk.SpeechConfig(
        subscription=SPEECH_KEY,
        region=SPEECH_REGION
    )

    speech_config.speech_synthesis_voice_name = voice

    audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name

    audio_config = speechsdk.audio.AudioOutputConfig(filename=audio_file)

    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    synthesizer.speak_text_async(text).get()

    return audio_file

# =========================
# MAIN UI
# =========================
st.markdown('<div class="card">', unsafe_allow_html=True)

text_input = st.text_area(
    "✍️ Enter your text",
    height=180,
    placeholder="Example: Hi, I am Somya Jain. Welcome to my AI project..."
)

col1, col2 = st.columns([1,1])

with col1:
    generate = st.button("🚀 Generate Speech")

with col2:
    clear = st.button("🧹 Clear")

if clear:
    st.experimental_rerun()

if generate:
    if text_input.strip() == "":
        st.warning("⚠️ Please enter text first")
    else:
        with st.spinner("⚡ Generating voice..."):
            audio_path = text_to_speech(text_input)

        st.success("✅ Audio Generated!")

        audio_file = open(audio_path, "rb")
        audio_bytes = audio_file.read()

        st.audio(audio_bytes, format="audio/wav")

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# FOOTER
# =========================
st.markdown("""
<div style="text-align:center;margin-top:40px;color:#777;">
🚀 Built with Streamlit + Azure AI <br>
✨ By Somya Jain
</div>
""", unsafe_allow_html=True)
