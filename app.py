import streamlit as st
import azure.cognitiveservices.speech as speechsdk
from PIL import Image
import pytesseract
import tempfile
import cv2
import numpy as np

# =========================
# AZURE CONFIG (KEEP SAME)
# =========================
SPEECH_KEY = "2LNcNfQUrK6f0jj3eZ1ssHm1qALaeiXmn1foajdEdGGo9bxH06i5JQQJ99CEACYeBjFXJ3w3AAAYACOGrjDr"
SPEECH_REGION = "eastus"

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="AI Image Narrator",
    layout="wide",
    page_icon="🎧"
)

# =========================
# DARK FUTURISTIC UI
# =========================
st.markdown("""
<style>

body {
    background: radial-gradient(circle at top, #0b0b12, #05060a);
    color: white;
}

/* HERO */
.hero {
    text-align: center;
    padding: 20px;
}

.hero h1 {
    font-size: 40px;
    background: linear-gradient(90deg, #7c3aed, #06b6d4, #ff2d95);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: glow 3s infinite alternate;
}

@keyframes glow {
    from { filter: drop-shadow(0 0 5px #7c3aed); }
    to { filter: drop-shadow(0 0 20px #06b6d4); }
}

.upload-box {
    border: 2px dashed #7c3aed;
    border-radius: 20px;
    padding: 30px;
    text-align: center;
    background: rgba(255,255,255,0.03);
    transition: 0.3s;
}

.upload-box:hover {
    border-color: #06b6d4;
    box-shadow: 0 0 20px #7c3aed;
    transform: scale(1.02);
}

.card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    padding: 20px;
    border-radius: 20px;
    backdrop-filter: blur(10px);
    box-shadow: 0 0 25px rgba(124,58,237,0.2);
}

button {
    background: linear-gradient(90deg, #7c3aed, #06b6d4);
    color: white;
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.markdown("""
<div class="hero">
    <h1>Transform Images into Natural Speech using AI</h1>
    <p>Cyber AI Studio • Smart Vision to Voice Engine</p>
</div>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR CONTROLS
# =========================
st.sidebar.title("⚙️ AI Controls")

voice = st.sidebar.selectbox(
    "Voice",
    ["en-US-JennyNeural", "en-IN-NeerjaNeural"]
)

speed = st.sidebar.slider("Speed", 0.5, 2.0, 1.0)

# =========================
# OCR FIX (IMPORTANT PART)
# =========================
def extract_text(image):
    img = np.array(image)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # noise removal
    blur = cv2.GaussianBlur(gray, (3,3), 0)

    # threshold for better text detection
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # OCR config (VERY IMPORTANT)
    config = r'--oem 3 --psm 6'

    text = pytesseract.image_to_string(thresh, config=config)

    return text

# =========================
# TEXT TO SPEECH
# =========================
def speak(text):
    speech_config = speechsdk.SpeechConfig(
        subscription=SPEECH_KEY,
        region=SPEECH_REGION
    )

    speech_config.speech_synthesis_voice_name = voice
    speech_config.set_speech_synthesis_rate(str(speed))

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        file = f.name

    audio_config = speechsdk.audio.AudioOutputConfig(filename=file)

    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    synthesizer.speak_text_async(text).get()

    return file

# =========================
# MAIN UI
# =========================
st.markdown('<div class="card">', unsafe_allow_html=True)

uploaded_file = st.file_uploader("📤 Upload Image (Drag & Drop Enabled)", type=["png","jpg","jpeg"])

if uploaded_file:

    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    if st.button("🚀 Analyze Image & Convert to Speech"):

        with st.spinner("🧠 AI is analyzing image..."):

            text = extract_text(image)

            # fallback fix
            if len(text.strip()) < 2:
                st.error("❌ No proper text detected. Try clearer image.")
            else:
                st.success("📝 Extracted Text")
                st.write(text)

                audio = speak(text)

                st.audio(audio)

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# FOOTER
# =========================
st.markdown("""
<div style="text-align:center; margin-top:30px; color:#aaa;">
✨ Developed by Somya Jain
</div>
""", unsafe_allow_html=True)
