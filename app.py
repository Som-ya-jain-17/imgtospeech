import streamlit as st
import azure.cognitiveservices.speech as speechsdk
from PIL import Image
import pytesseract
import tempfile
import cv2
import numpy as np
import re

# =========================
# AZURE CONFIG (UNCHANGED)
# =========================
SPEECH_KEY = "2LNcNfQUrK6f0jj3eZ1ssHm1qALaeiXmn1foajdEdGGo9bxH06i5JQQJ99CEACYeBjFXJ3w3AAAYACOGrjDr"
SPEECH_REGION = "eastus"

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="AI Image to Speech", layout="wide")

# =========================
# SIMPLE DARK UI
# =========================
st.markdown("""
<style>
body {
    background-color: #0b0f1a;
    color: white;
}
.title {
    text-align:center;
    font-size:40px;
    font-weight:bold;
    color:#7c3aed;
}
.card {
    background: rgba(255,255,255,0.05);
    padding:20px;
    border-radius:15px;
    margin-top:10px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🎧 AI Image → Speech Converter</div>', unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================
lang = st.sidebar.selectbox("Language", ["English", "Hindi"])

voice_map = {
    "English": "en-US-JennyNeural",
    "Hindi": "hi-IN-SwaraNeural"
}

VOICE = voice_map[lang]

# =========================
# CLEAN TEXT (IMPORTANT FIX)
# =========================
def clean_text(text):
    text = text.replace("\n", " ")
    text = " ".join(text.split())
    text = re.sub(r'(.)\1{2,}', r'\1', text)  # hiii → hi
    return text

# =========================
# OCR FUNCTION (STABLE)
# =========================
def extract_text(image):
    img = np.array(image)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # improve readability
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
# AZURE SPEECH (CORRECT WAY)
# =========================
def speak(text):

    speech_config = speechsdk.SpeechConfig(
        subscription=SPEECH_KEY,
        region=SPEECH_REGION
    )

    speech_config.speech_synthesis_voice_name = VOICE

    # output file
    audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    audio_config = speechsdk.audio.AudioOutputConfig(filename=audio_file)

    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    synthesizer.speak_text_async(text).get()

    return audio_file

# =========================
# UI
# =========================
st.markdown('<div class="card">', unsafe_allow_html=True)

uploaded_file = st.file_uploader("📤 Upload Image", type=["png", "jpg", "jpeg"])

if uploaded_file:

    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    if st.button("🚀 Convert to Speech"):

        raw_text = extract_text(image)
        text = clean_text(raw_text)

        if text.strip() == "":
            st.error("❌ No text detected. Try a clearer image.")
        else:
            st.success("📝 Extracted Text")
            st.write(text)

            audio_path = speak(text)

            # FIX: Streamlit audio always works like this
            with open(audio_path, "rb") as f:
                st.audio(f.read(), format="audio/wav")

st.markdown("</div>", unsafe_allow_html=True)

# =========================
# FOOTER
# =========================
st.markdown("""
<div style="text-align:center;color:gray;margin-top:30px;">
✨ Developed by Somya Jain
</div>
""", unsafe_allow_html=True)
