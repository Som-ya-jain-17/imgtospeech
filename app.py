import streamlit as st
import azure.cognitiveservices.speech as speechsdk
from PIL import Image
import pytesseract
import tempfile
import cv2
import numpy as np

# =========================
# AZURE CONFIG (YOUR KEYS)
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
# 🌌 PURE DARK FUTURISTIC UI
# =========================
st.markdown("""
<style>

/* MAIN BACKGROUND */
html, body, [data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at top, #05060a, #0b0f1a, #05060a);
    color: white;
}

/* Animated glow overlay */
.stApp::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: radial-gradient(circle at 20% 20%, rgba(124,58,237,0.15),
                transparent 40%),
                radial-gradient(circle at 80% 30%, rgba(6,182,212,0.12),
                transparent 40%),
                radial-gradient(circle at 50% 80%, rgba(255,45,149,0.10),
                transparent 40%);
    z-index: -1;
}

/* HERO TITLE */
.hero {
    text-align: center;
    padding: 10px;
}

.hero h1 {
    font-size: 42px;
    font-weight: bold;
    background: linear-gradient(90deg, #7c3aed, #06b6d4, #ff2d95);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 0 25px rgba(124,58,237,0.4);
}

/* GLASS CARD */
.card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(18px);
    border-radius: 18px;
    padding: 20px;
    border: 1px solid rgba(124,58,237,0.2);
    box-shadow: 0 0 30px rgba(124,58,237,0.15);
    margin-top: 10px;
}

/* BUTTON */
.stButton>button {
    background: linear-gradient(90deg, #7c3aed, #06b6d4);
    color: white;
    border-radius: 12px;
    padding: 10px 20px;
    border: none;
    box-shadow: 0 0 15px rgba(6,182,212,0.4);
}

.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 25px rgba(255,45,149,0.5);
}

/* FILE UPLOADER */
[data-testid="stFileUploader"] {
    border: 2px dashed #7c3aed;
    border-radius: 15px;
    padding: 10px;
}

/* TEXT AREA DARK */
textarea {
    background: rgba(255,255,255,0.05) !important;
    color: white !important;
}

/* FOOTER */
.footer {
    text-align: center;
    color: #aaa;
    margin-top: 30px;
}

</style>
""", unsafe_allow_html=True)

# =========================
# HERO SECTION
# =========================
st.markdown("""
<div class="hero">
    <h1>🎧 AI Image to Speech Converter</h1>
    <p>Turn images into natural voice using Azure AI</p>
</div>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================
st.sidebar.title("⚙️ Controls")

voice = st.sidebar.selectbox(
    "Voice",
    ["en-US-JennyNeural", "en-IN-NeerjaNeural"]
)

speed = st.sidebar.slider("Speed", 0.5, 2.0, 1.0)

# =========================
# OCR (FIXED + STRONG)
# =========================
def extract_text(image):
    img = np.array(image)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # improve contrast
    gray = cv2.convertScaleAbs(gray, alpha=1.8, beta=10)

    # remove noise
    blur = cv2.GaussianBlur(gray, (3,3), 0)

    # threshold
    thresh = cv2.adaptiveThreshold(
        blur, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11, 2
    )

    config = r'--oem 3 --psm 6'

    return pytesseract.image_to_string(thresh, config=config)

# =========================
# TEXT TO SPEECH (FIXED AZURE)
# =========================
def speak(text):
    speech_config = speechsdk.SpeechConfig(
        subscription=SPEECH_KEY,
        region=SPEECH_REGION
    )

    speech_config.speech_synthesis_voice_name = voice

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        filename = f.name

    audio_config = speechsdk.audio.AudioOutputConfig(filename=filename)

    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    # SSML (correct way for speed control)
    rate = int((speed - 1.0) * 100)

    ssml = f"""
    <speak version='1.0' xml:lang='en-US'>
        <voice name='{voice}'>
            <prosody rate='{rate}%'>
                {text}
            </prosody>
        </voice>
    </speak>
    """

    synthesizer.speak_ssml_async(ssml).get()

    return filename

# =========================
# MAIN APP
# =========================
st.markdown('<div class="card">', unsafe_allow_html=True)

uploaded_file = st.file_uploader("📤 Upload Image", type=["png", "jpg", "jpeg"])

if uploaded_file:

    image = Image.open(uploaded_file)

    col1, col2 = st.columns(2)

    with col1:
        st.image(image, caption="Uploaded Image", use_container_width=True)

    with col2:
        if st.button("🚀 Generate Speech"):

            with st.spinner("🧠 AI Processing Image..."):

                text = extract_text(image)

                if not text.strip():
                    st.error("❌ No clear text found. Try a clearer image.")
                else:
                    st.success("📝 Extracted Text")
                    st.write(text)

                    audio = speak(text)

                    st.audio(audio)

st.markdown("</div>", unsafe_allow_html=True)

# =========================
# FOOTER
# =========================
st.markdown("""
<div class="footer">
✨ Developed by Somya Jain
</div>
""", unsafe_allow_html=True)
