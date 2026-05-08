import streamlit as st
import azure.cognitiveservices.speech as speechsdk
from PIL import Image
import pytesseract
import tempfile
import cv2
import numpy as np
import re
import time
from datetime import datetime

# =========================
# AZURE CONFIG (UNCHANGED)
# =========================
SPEECH_KEY = "2LNcNfQUrK6f0jj3eZ1ssHm1qALaeiXmn1foajdEdGGo9bxH06i5JQQJ99CEACYeBjFXJ3w3AAAYACOGrjDr"
SPEECH_REGION = "eastus"

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="AI Image Voice Pro",
    layout="wide",
    page_icon="🎧"
)

# =========================
# HISTORY STORAGE (SAFE ADDITION)
# =========================
if "history" not in st.session_state:
    st.session_state.history = []

# =========================
# 🎨 PREMIUM DARK UI
# =========================
st.markdown("""
<style>

/* DARK BACKGROUND */
.stApp {
    background: radial-gradient(circle at top, #05060a, #0a0f1a, #05060a);
    color: white;
}

/* TITLE */
.title {
    text-align: center;
    font-size: 42px;
    font-weight: 800;
    background: linear-gradient(90deg,#7c3aed,#06b6d4,#ff2d95);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* GLASS CARD */
.card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(18px);
    border-radius: 18px;
    padding: 18px;
    border: 1px solid rgba(124,58,237,0.25);
    box-shadow: 0 0 25px rgba(124,58,237,0.2);
    margin-bottom: 15px;
}

/* BUTTON */
.stButton>button {
    background: linear-gradient(90deg,#7c3aed,#06b6d4);
    color: white;
    border-radius: 10px;
    padding: 10px 15px;
    border: none;
    box-shadow: 0 0 15px rgba(6,182,212,0.4);
}

.stButton>button:hover {
    transform: scale(1.03);
}

/* UPLOADER */
[data-testid="stFileUploader"] {
    border: 2px dashed #7c3aed;
    border-radius: 15px;
    padding: 10px;
}

/* AUDIO */
audio {
    width: 100%;
    border-radius: 10px;
    filter: drop-shadow(0 0 10px cyan);
}

</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.markdown('<div class="title">🎧 AI Image → Speech Converter Pro</div>', unsafe_allow_html=True)
st.write("Upload image → Extract text → Listen in AI voice")

# =========================
# SIDEBAR CONTROLS (SAFE EXTENSION)
# =========================
st.sidebar.title("⚙️ AI Controls")

language = st.sidebar.selectbox("Language", ["English", "Hindi"])
emotion = st.sidebar.selectbox("Emotion Mode", ["Neutral", "Happy", "Calm", "Storytelling", "Robot"])

voice_map = {
    "English": "en-US-JennyNeural",
    "Hindi": "hi-IN-SwaraNeural"
}

voice = voice_map[language]

speed = st.sidebar.slider("Speech Speed", 0.5, 2.0, 1.0)

# =========================
# 🧠 TEXT CLEANING (MAIN FIX)
# =========================
def clean_text(text):
    text = text.replace("\n", " ")
    text = " ".join(text.split())
    text = re.sub(r'(.)\1{2,}', r'\1', text)  # hiii → hi
    return text

# =========================
# OCR (IMPROVED BUT SAFE)
# =========================
def extract_text(image):
    img = np.array(image)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3,3), 0)

    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11, 2
    )

    config = r'--oem 3 --psm 6'

    text = pytesseract.image_to_string(thresh, config=config)

    return text

# =========================
# SPEECH (FIXED + STABLE)
# =========================
def speak(text):

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

    # SSML for speed control
    rate = int((speed - 1.0) * 100)

    ssml = f"""
    <speak version='1.0'>
        <voice name='{voice}'>
            <prosody rate='{rate}%'>
                {text}
            </prosody>
        </voice>
    </speak>
    """

    synthesizer.speak_ssml_async(ssml).get()

    return audio_file

# =========================
# MAIN UI
# =========================
st.markdown('<div class="card">', unsafe_allow_html=True)

uploaded_file = st.file_uploader("📤 Upload Image", type=["png", "jpg", "jpeg"])

if uploaded_file:

    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    if st.button("🚀 Convert to Speech"):

        with st.spinner("🧠 AI Processing..."):

            raw_text = extract_text(image)

            text = clean_text(raw_text)

            if not text.strip():
                st.error("❌ No readable text found")
            else:
                st.success("📝 Extracted Text")
                st.write(text)

                audio = speak(text)

                with open(audio, "rb") as f:
                    st.audio(f.read(), format="audio/wav")

                # =========================
                # HISTORY SAVE (SAFE ADDITION)
                # =========================
                st.session_state.history.append({
                    "text": text,
                    "time": datetime.now().strftime("%H:%M:%S")
                })

st.markdown("</div>", unsafe_allow_html=True)

# =========================
# HISTORY SECTION (NEW FEATURE)
# =========================
st.markdown("### 📜 History")

for item in reversed(st.session_state.history[-5:]):
    st.markdown(f"""
    <div class="card">
        ⏱️ {item['time']} <br>
        📝 {item['text']}
    </div>
    """, unsafe_allow_html=True)

# =========================
# FOOTER
# =========================
st.markdown("""
<div style="text-align:center;color:#888;margin-top:30px;">
✨ Developed by Somya Jain
</div>
""", unsafe_allow_html=True)
