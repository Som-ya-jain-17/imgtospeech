import streamlit as st
import azure.cognitiveservices.speech as speechsdk
from PIL import Image
import pytesseract
import tempfile
import cv2
import numpy as np

# ---------------------------
# Azure Config (UNCHANGED)
# ---------------------------
SPEECH_KEY = "2LNcNfQUrK6f0jj3eZ1ssHm1qALaeiXmn1foajdEdGGo9bxH06i5JQQJ99CEACYeBjFXJ3w3AAAYACOGrjDr"
SPEECH_REGION = "eastus"

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(page_title="AI Image Narrator", layout="wide")

# ---------------------------
# UI (Glassmorphism + Gradient)
# ---------------------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #667eea, #764ba2);
}
.main-card {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(15px);
    padding: 30px;
    border-radius: 20px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}
h1 {
    text-align: center;
    color: white;
}
.tagline {
    text-align: center;
    color: #ddd;
}
.stButton>button {
    background: linear-gradient(90deg, #ff7eb3, #ff758c);
    color: white;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Header
# ---------------------------
st.markdown("<h1>🎧 AI Image Narrator</h1>", unsafe_allow_html=True)
st.markdown('<p class="tagline">Turn images into meaningful audio instantly</p>', unsafe_allow_html=True)

# ---------------------------
# Sidebar (Settings)
# ---------------------------
st.sidebar.title("⚙️ AI Settings")

voice = st.sidebar.selectbox(
    "Voice",
    ["en-US-JennyNeural", "en-IN-NeerjaNeural"]
)

speed = st.sidebar.slider("Speech Speed", 0.5, 2.0, 1.0)

# ---------------------------
# OCR FUNCTION (FIXED)
# ---------------------------
def extract_text(image):
    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Improve OCR accuracy
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )

    return pytesseract.image_to_string(thresh, config="--psm 6")

# ---------------------------
# Speech Function
# ---------------------------
def text_to_speech(text):
    speech_config = speechsdk.SpeechConfig(
        subscription=SPEECH_KEY,
        region=SPEECH_REGION
    )
    speech_config.speech_synthesis_voice_name = voice
    speech_config.set_speech_synthesis_rate(str(speed))

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        filename = f.name

    audio_config = speechsdk.audio.AudioOutputConfig(filename=filename)

    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    synthesizer.speak_text_async(text).get()
    return filename

# ---------------------------
# Main Card
# ---------------------------
st.markdown('<div class="main-card">', unsafe_allow_html=True)

uploaded_file = st.file_uploader("📤 Drag & Drop Image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)

    col1, col2 = st.columns(2)

    with col1:
        st.image(image, caption="Uploaded Image")

    with col2:
        if st.button("🚀 Analyze & Convert"):
            with st.spinner("🤖 AI is analyzing image..."):

                text = extract_text(image)

                if text.strip() == "":
                    st.error("⚠️ Couldn't detect text. Try clearer image.")
                else:
                    st.success("📝 Extracted Text")
                    st.write(text)

                    audio = text_to_speech(text)

                    st.audio(audio)

                    with open(audio, "rb") as f:
                        st.download_button(
                            "⬇️ Download Audio",
                            f,
                            file_name="speech.wav"
                        )

st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# Footer
# ---------------------------
st.markdown(
    "<p style='text-align:center;color:white;margin-top:20px;'>✨ Developed by Somya Jain</p>",
    unsafe_allow_html=True
)
