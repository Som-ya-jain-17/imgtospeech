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
# 🌌 ADVANCED UI (NEON + DARK)
# ---------------------------
st.markdown("""
<style>
body {
    background: #0f0f1a;
    color: white;
}

/* Hero Section */
.hero {
    text-align: center;
    padding: 30px;
}
.hero h1 {
    font-size: 48px;
    font-weight: bold;
    background: linear-gradient(90deg, #ff00cc, #3333ff, #00ffff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero p {
    color: #aaa;
}

/* Cards */
.card {
    background: rgba(255,255,255,0.05);
    border-radius: 20px;
    padding: 20px;
    backdrop-filter: blur(10px);
    box-shadow: 0 0 20px rgba(255,0,255,0.2);
    transition: 0.3s;
}
.card:hover {
    transform: scale(1.02);
    box-shadow: 0 0 30px rgba(0,255,255,0.5);
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #ff00cc, #3333ff);
    color: white;
    border-radius: 12px;
    border: none;
    padding: 10px 20px;
    box-shadow: 0 0 15px #ff00cc;
}
.stButton>button:hover {
    box-shadow: 0 0 25px #00ffff;
}

/* Upload box */
.upload-box {
    border: 2px dashed #00ffff;
    padding: 30px;
    border-radius: 20px;
    text-align: center;
    transition: 0.3s;
}
.upload-box:hover {
    border-color: #ff00cc;
    box-shadow: 0 0 20px #ff00cc;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #121212;
}

/* Audio */
audio {
    width: 100%;
    filter: drop-shadow(0 0 10px cyan);
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# 🌟 HERO
# ---------------------------
st.markdown("""
<div class="hero">
<h1>🚀 Turn Images Into Voice with AI</h1>
<p>Upload an image → Extract text → Listen instantly 🎧</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------
# ⚙️ SIDEBAR
# ---------------------------
st.sidebar.title("⚙️ AI Controls")

voice = st.sidebar.selectbox(
    "🎤 Voice",
    ["en-US-JennyNeural", "en-IN-NeerjaNeural"]
)

speed = st.sidebar.slider("⚡ Speed", 0.5, 2.0, 1.0)

# ---------------------------
# 🧠 OCR FUNCTION (FIXED)
# ---------------------------
def extract_text(image):
    img = np.array(image)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    return pytesseract.image_to_string(thresh, config="--psm 6")

# ---------------------------
# 🔊 TEXT TO SPEECH (FIXED)
# ---------------------------
def text_to_speech(text):
    speech_config = speechsdk.SpeechConfig(
        subscription=SPEECH_KEY,
        region=SPEECH_REGION
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        filename = f.name

    audio_config = speechsdk.audio.AudioOutputConfig(filename=filename)

    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

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

# ---------------------------
# 📤 UPLOAD SECTION
# ---------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)

uploaded_file = st.file_uploader("📤 Drag & Drop Image", type=["jpg", "png", "jpeg"])

st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# 📸 IMAGE + OUTPUT
# ---------------------------
if uploaded_file:
    image = Image.open(uploaded_file)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.image(image, caption="📸 Uploaded Image")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        if st.button("🚀 Analyze Image"):
            progress = st.progress(0)

            for i in range(100):
                progress.progress(i + 1)

            st.info("🤖 Analyzing Image...")

            text = extract_text(image)

            if text.strip() == "":
                st.error("⚠️ No readable text found")
            else:
                st.success("📝 Extracted Text")
                st.write(text)

                audio = text_to_speech(text)

                st.audio(audio)

                with open(audio, "rb") as f:
                    st.download_button("⬇️ Download Audio", f, "speech.wav")

        st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# ✨ FOOTER
# ---------------------------
st.markdown(
    "<p style='text-align:center;margin-top:40px;color:#888;'>✨ Developed by Somya Jain</p>",
    unsafe_allow_html=True
)
