import streamlit as st
import azure.cognitiveservices.speech as speechsdk
import pytesseract
from PIL import Image
import tempfile
import base64

# =========================
# AZURE CONFIG
# =========================
SPEECH_KEY = "2LNcNfQUrK6f0jj3eZ1ssHm1qALaeiXmn1foajdEdGGo9bxH06i5JQQJ99CEACYeBjFXJ3w3AAAYACOGrjDr"
SPEECH_REGION = "eastus"

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="AI Speech Studio", layout="wide")

# =========================
# 💎 ULTRA PREMIUM UI
# =========================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#04050a,#0a0f1a,#04050a);
    color:white;
}

/* TITLE */
.title {
    text-align:center;
    font-size:48px;
    font-weight:900;
    background: linear-gradient(90deg,#8b5cf6,#06b6d4,#ff2d95);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}

/* CARD */
.card {
    background: rgba(255,255,255,0.05);
    padding:25px;
    border-radius:20px;
    backdrop-filter:blur(20px);
    border:1px solid rgba(139,92,246,0.3);
}

/* BUTTON */
.stButton>button {
    background: linear-gradient(90deg,#8b5cf6,#06b6d4,#ff2d95);
    color:white;
    border-radius:12px;
    padding:10px 18px;
    border:none;
}

/* TEXT */
textarea {
    background:#0b0f1a !important;
    color:white !important;
}
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.markdown('<div class="title">🎧 AI Speech Studio</div>', unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================
st.sidebar.header("⚙️ Controls")

voice = st.sidebar.selectbox(
    "Voice",
    ["en-US-JennyNeural", "en-IN-NeerjaNeural"]
)

speed = st.sidebar.slider("Speech Speed", 0.5, 2.0, 1.0)

# =========================
# TEXT → SPEECH FUNCTION
# =========================
def text_to_speech(text):
    speech_config = speechsdk.SpeechConfig(
        subscription=SPEECH_KEY,
        region=SPEECH_REGION
    )

    speech_config.speech_synthesis_voice_name = voice

    # Apply speed using SSML
    ssml = f"""
    <speak version='1.0' xml:lang='en-US'>
        <voice name='{voice}'>
            <prosody rate='{speed}'>
                {text}
            </prosody>
        </voice>
    </speak>
    """

    audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name

    audio_config = speechsdk.audio.AudioOutputConfig(filename=audio_file)

    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    synthesizer.speak_ssml_async(ssml).get()

    return audio_file

# =========================
# OCR FUNCTION
# =========================
def extract_text_from_image(image):
    text = pytesseract.image_to_string(image)
    return text

# =========================
# MAIN UI
# =========================
st.markdown('<div class="card">', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["✍️ Text Input", "🖼️ Image Upload"])

# -------- TEXT TAB --------
with tab1:
    text_input = st.text_area("Enter Text", height=150)

    if st.button("🚀 Convert Text to Speech"):
        if text_input.strip() == "":
            st.warning("Enter text first")
        else:
            audio_path = text_to_speech(text_input)

            audio_bytes = open(audio_path, "rb").read()
            st.audio(audio_bytes)

            # download
            st.download_button("⬇️ Download Audio", audio_bytes, "speech.wav")

# -------- IMAGE TAB --------
with tab2:
    uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image")

        if st.button("🔍 Extract Text"):
            extracted_text = extract_text_from_image(image)

            st.text_area("Extracted Text", extracted_text, height=150)

            if extracted_text.strip():
                if st.button("🎧 Convert Extracted Text to Speech"):
                    audio_path = text_to_speech(extracted_text)

                    audio_bytes = open(audio_path, "rb").read()
                    st.audio(audio_bytes)

                    st.download_button("⬇️ Download Audio", audio_bytes, "image_speech.wav")

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# FOOTER
# =========================
st.markdown("""
<div style="text-align:center;margin-top:30px;color:#777;">
✨ AI Powered Speech + Vision App | By Somya Jain
</div>
""", unsafe_allow_html=True)
