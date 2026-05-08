import streamlit as st
import azure.cognitiveservices.speech as speechsdk
from PIL import Image
import pytesseract
import tempfile
import numpy as np
import cv2

# ---------------------------
# AZURE CONFIG (YOUR KEY)
# ---------------------------
SPEECH_KEY = "2LNcNfQUrK6f0jj3eZ1ssHm1qALaeiXmn1foajdEdGGo9bxH06i5JQQJ99CEACYeBjFXJ3w3AAAYACOGrjDr"
SPEECH_REGION = "eastus"

# ---------------------------
# Tesseract PATH (IMPORTANT)
# ---------------------------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="AI Speech Studio", page_icon="🎙️", layout="centered")

# ---------------------------
# PREMIUM DARK UI
# ---------------------------
st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #0b0f1a, #0f172a, #1a1b2e);
    color: white;
}

.title {
    text-align: center;
    font-size: 44px;
    font-weight: 900;
    background: linear-gradient(90deg, #00f5ff, #a855f7, #ff00cc, #00ff88);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Glossy Buttons */
.stButton>button {
    background: linear-gradient(135deg, #00f5ff, #7c3aed, #ff00cc);
    color: white;
    border-radius: 14px;
    padding: 0.6rem 1.2rem;
    font-weight: bold;
    border: none;
    box-shadow: 0 0 20px rgba(0,255,255,0.3);
    transition: 0.3s;
}

.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 30px rgba(255,0,200,0.5);
}

/* Text Area */
textarea {
    background-color: #111827 !important;
    color: white !important;
    border-radius: 12px !important;
}

/* File uploader */
section[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 10px;
}

/* Tabs */
.stTabs [data-baseweb="tab"] {
    background: rgba(255,255,255,0.05);
    color: white;
    border-radius: 10px;
}

.footer {
    text-align: center;
    margin-top: 40px;
    color: gray;
}

</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🎙️ AI Image & Text to Speech Studio</div>', unsafe_allow_html=True)
st.write("Convert text or images into natural speech using Azure AI 🚀")

# ---------------------------
# TEXT TO SPEECH
# ---------------------------
def text_to_speech(text):
    speech_config = speechsdk.SpeechConfig(
        subscription=SPEECH_KEY,
        region=SPEECH_REGION
    )

    speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        audio_path = f.name

    audio_config = speechsdk.audio.AudioOutputConfig(filename=audio_path)

    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    synthesizer.speak_text_async(text).get()

    return audio_path

# ---------------------------
# OCR FUNCTION (FIXED + PREPROCESSING)
# ---------------------------
def extract_text(image):
    img = np.array(image)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5,5), 0)
    gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(gray, config=config)

    return text

# ---------------------------
# TABS
# ---------------------------
tab1, tab2 = st.tabs(["📝 Text to Speech", "🖼️ Image to Speech"])

# ---------------------------
# TEXT TAB
# ---------------------------
with tab1:
    st.subheader("Enter Text")
    user_text = st.text_area("Type here...", height=150)

    if st.button("🔊 Convert to Speech"):
        if user_text.strip():
            audio = text_to_speech(user_text)
            st.audio(audio)
        else:
            st.warning("Please enter text")

# ---------------------------
# IMAGE TAB
# ---------------------------
with tab2:
    st.subheader("Upload Image")
    uploaded_file = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image")

        if st.button("🔍 Extract & Speak"):
            text = extract_text(image)

            if text.strip():
                st.success("Extracted Text")
                st.write(text)

                audio = text_to_speech(text)
                st.audio(audio)
            else:
                st.error("No text found. Use clearer image.")

# ---------------------------
# FOOTER
# ---------------------------
st.markdown('<div class="footer">✨ Developed by Somya Jain</div>', unsafe_allow_html=True)
