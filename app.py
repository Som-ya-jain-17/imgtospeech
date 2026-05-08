import streamlit as st
import azure.cognitiveservices.speech as speechsdk
from PIL import Image
import pytesseract
import tempfile
import numpy as np

# ---------------------------
# AZURE CONFIG
# ---------------------------
SPEECH_KEY = "2LNcNfQUrK6f0jj3eZ1ssHm1qALaeiXmn1foajdEdGGo9bxH06i5JQQJ99CEACYeBjFXJ3w3AAAYACOGrjDr"
SPEECH_REGION = "eastus"

# ---------------------------
# SAFE OCR (NO CV2 = NO ERRORS)
# ---------------------------
def extract_text(image):
    return pytesseract.image_to_string(image)

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
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="AI Speech Studio", page_icon="🎙️", layout="centered")

# ---------------------------
# PREMIUM DARK GLASS UI
# ---------------------------
st.markdown("""
<style>

/* Background */
.stApp {
    background: radial-gradient(circle at top, #0f172a, #050816, #000000);
    color: white;
}

/* Main Title */
.title {
    text-align: center;
    font-size: 44px;
    font-weight: 900;
    background: linear-gradient(90deg, #00f5ff, #a855f7, #ff00cc, #00ff88);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 10px;
}

/* Subtitle */
.subtitle {
    text-align: center;
    color: #aaa;
    font-size: 16px;
    margin-bottom: 30px;
}

/* Glass card effect */
.block-container {
    padding: 2rem;
}

/* Tabs styling */
.stTabs [data-baseweb="tab"] {
    background: rgba(255,255,255,0.05);
    border-radius: 12px;
    color: white;
}

/* Text area */
textarea {
    background-color: rgba(255,255,255,0.05) !important;
    color: white !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.1);
}

/* File uploader */
section[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 10px;
    border: 1px solid rgba(255,255,255,0.1);
}

/* Premium glossy button */
.stButton>button {
    background: linear-gradient(135deg, #00f5ff, #7c3aed, #ff00cc);
    color: white;
    border-radius: 14px;
    padding: 0.6rem 1.2rem;
    font-weight: bold;
    border: none;
    box-shadow: 0 0 20px rgba(0,255,255,0.25);
    transition: 0.3s ease;
}

.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 35px rgba(255,0,200,0.5);
}

/* Footer */
.footer {
    text-align: center;
    margin-top: 40px;
    color: gray;
    font-size: 13px;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------
# HEADER
# ---------------------------
st.markdown('<div class="title">🎙️ AI Speech Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Image → Text → Speech | Powered by Azure AI</div>', unsafe_allow_html=True)

# ---------------------------
# TABS
# ---------------------------
tab1, tab2 = st.tabs(["📝 Text to Speech", "🖼️ Image to Speech"])

# ---------------------------
# TEXT TAB
# ---------------------------
with tab1:
    st.subheader("Enter Your Text")
    user_text = st.text_area("Type something...", height=150)

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
    file = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"])

    if file:
        img = Image.open(file)
        st.image(img, caption="Uploaded Image", use_container_width=True)

        if st.button("🔍 Extract & Speak"):
            text = extract_text(img)

            if text.strip():
                st.success("Extracted Text")
                st.write(text)

                audio = text_to_speech(text)
                st.audio(audio)
            else:
                st.error("No text found in image")

# ---------------------------
# FOOTER
# ---------------------------
st.markdown('<div class="footer">✨ Developed by Somya Jain</div>', unsafe_allow_html=True)
