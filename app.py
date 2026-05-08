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
# UI
# =========================
st.set_page_config(page_title="AI Image to Speech", layout="wide")

st.title("🎧 AI Image → Speech Converter")

lang = st.sidebar.selectbox("Language", ["English", "Hindi"])

voice_map = {
    "English": "en-US-JennyNeural",
    "Hindi": "hi-IN-SwaraNeural"
}

VOICE = voice_map[lang]

# =========================
# CLEAN TEXT (IMPORTANT)
# =========================
def clean_text(text):
    text = text.replace("\n", " ")
    text = " ".join(text.split())
    text = re.sub(r'(.)\1{2,}', r'\1', text)
    return text

# =========================
# 🔥 FIXED OCR (MAIN UPGRADE)
# =========================
def extract_text(image):

    img = np.array(image)

    # 1. upscale image (VERY IMPORTANT)
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # 2. grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 3. denoise
    gray = cv2.bilateralFilter(gray, 9, 75, 75)

    # 4. adaptive threshold (better text detection)
    thresh = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        2
    )

    # 5. BEST OCR CONFIG (CRITICAL FIX)
    config = r'--oem 3 --psm 4'

    text = pytesseract.image_to_string(thresh, config=config)

    return text

# =========================
# AZURE SPEECH (UNCHANGED)
# =========================
def speak(text):

    speech_config = speechsdk.SpeechConfig(
        subscription=SPEECH_KEY,
        region=SPEECH_REGION
    )

    speech_config.speech_synthesis_voice_name = VOICE

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
file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

if file:

    image = Image.open(file)
    st.image(image, caption="Uploaded Image")

    if st.button("Convert to Speech"):

        raw_text = extract_text(image)

        text = clean_text(raw_text)

        st.subheader("Extracted Text")
        st.write(text)

        if text.strip() == "":
            st.error("No text detected clearly. Try a sharper image.")
        else:
            audio = speak(text)

            with open(audio, "rb") as f:
                st.audio(f.read(), format="audio/wav")
