import streamlit as st
import azure.cognitiveservices.speech as speechsdk
from PIL import Image
import pytesseract
import tempfile
import cv2
import numpy as np
import re

# =========================
# AZURE (UNCHANGED)
# =========================
SPEECH_KEY = "2LNcNfQUrK6f0jj3eZ1ssHm1qALaeiXmn1foajdEdGGo9bxH06i5JQQJ99CEACYeBjFXJ3w3AAAYACOGrjDr"
SPEECH_REGION = "eastus"

# =========================
# DARK UI (FIXED + CLEAN)
# =========================
st.set_page_config(page_title="AI Image Speech", layout="wide")

st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top, #05060a, #0b0f1a, #05060a);
    color: white;
}

.title {
    text-align:center;
    font-size:40px;
    font-weight:bold;
    background: linear-gradient(90deg,#7c3aed,#06b6d4,#ff2d95);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.card {
    background: rgba(255,255,255,0.05);
    padding:20px;
    border-radius:15px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(124,58,237,0.3);
}

button {
    background: linear-gradient(90deg,#7c3aed,#06b6d4);
    color:white;
    border-radius:10px;
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
# CLEAN TEXT
# =========================
def clean_text(text):
    text = text.replace("\n", " ")
    text = " ".join(text.split())
    text = re.sub(r'(.)\1{2,}', r'\1', text)
    return text

# =========================
# 🔥 OCR FIX (MAIN UPGRADE)
# =========================
def extract_text(image):

    img = np.array(image)

    # 1. upscale image (CRITICAL FIX)
    img = cv2.resize(img, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)

    # 2. grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 3. denoise
    gray = cv2.fastNlMeansDenoising(gray, None, 30, 7, 21)

    # 4. sharpen
    kernel = np.array([[0,-1,0],
                       [-1,5,-1],
                       [0,-1,0]])
    sharp = cv2.filter2D(gray, -1, kernel)

    # 5. threshold
    thresh = cv2.adaptiveThreshold(
        sharp, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31, 2
    )

    # 🔥 BEST OCR CONFIG (IMPORTANT FIX)
    config = r'--oem 3 --psm 6'

    text = pytesseract.image_to_string(thresh, config=config)

    return text

# =========================
# SPEECH
# =========================
def speak(text):

    speech_config = speechsdk.SpeechConfig(
        subscription=SPEECH_KEY,
        region=SPEECH_REGION
    )

    speech_config.speech_synthesis_voice_name = VOICE

    file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    audio_config = speechsdk.audio.AudioOutputConfig(filename=file)

    synth = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    synth.speak_text_async(text).get()

    return file

# =========================
# UI
# =========================
st.markdown('<div class="card">', unsafe_allow_html=True)

file = st.file_uploader("Upload Image", type=["png","jpg","jpeg"])

if file:

    image = Image.open(file)
    st.image(image, caption="Uploaded Image")

    if st.button("Convert to Speech"):

        raw = extract_text(image)
        text = clean_text(raw)

        st.subheader("Extracted Text")
        st.write(text)

        if text.strip() == "":
            st.error("❌ Text not detected properly. Try clearer image.")
        else:
            audio = speak(text)

            with open(audio, "rb") as f:
                st.audio(f.read(), format="audio/wav")

st.markdown("</div>", unsafe_allow_html=True)
