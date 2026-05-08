import streamlit as st
import azure.cognitiveservices.speech as speechsdk
import pytesseract
from PIL import Image
import tempfile

# =========================
# CONFIG
# =========================
SPEECH_KEY = "2LNcNfQUrK6f0jj3eZ1ssHm1qALaeiXmn1foajdEdGGo9bxH06i5JQQJ99CEACYeBjFXJ3w3AAAYACOGrjDr"
SPEECH_REGION = "eastus"

# For Streamlit Cloud (IMPORTANT)
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

st.set_page_config(page_title="AI Speech Studio", layout="wide")

# =========================
# UI
# =========================
st.markdown("""
<style>
.stApp {background: linear-gradient(135deg,#05060a,#0a0f1a);}
.stButton>button {
    background: linear-gradient(90deg,#8b5cf6,#06b6d4,#ff2d95);
    color:white;
    border-radius:10px;
}
</style>
""", unsafe_allow_html=True)

st.title("🎧 AI Text & Image → Speech")

# =========================
# SESSION STATE (IMPORTANT FIX)
# =========================
if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = ""

# =========================
# SIDEBAR
# =========================
voice = st.sidebar.selectbox(
    "Voice",
    ["en-US-JennyNeural", "en-IN-NeerjaNeural"]
)

# =========================
# FUNCTION
# =========================
def text_to_speech(text):
    speech_config = speechsdk.SpeechConfig(
        subscription=SPEECH_KEY,
        region=SPEECH_REGION
    )

    speech_config.speech_synthesis_voice_name = voice

    audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name

    audio_config = speechsdk.audio.AudioOutputConfig(filename=audio_file)

    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    synthesizer.speak_text_async(text).get()

    return audio_file

# =========================
# TABS
# =========================
tab1, tab2 = st.tabs(["✍️ Text", "🖼️ Image"])

# -------- TEXT TAB --------
with tab1:
    text_input = st.text_area("Enter text")

    if st.button("🚀 Convert Text"):
        if text_input.strip():
            audio_path = text_to_speech(text_input)
            audio_bytes = open(audio_path, "rb").read()
            st.audio(audio_bytes)
        else:
            st.warning("Enter text first")

# -------- IMAGE TAB --------
with tab2:
    uploaded_file = st.file_uploader("Upload image", type=["png","jpg","jpeg"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image")

        # Extract text button
        if st.button("🔍 Extract Text"):
            st.session_state.extracted_text = pytesseract.image_to_string(image)

        # Show extracted text
        st.text_area("Extracted Text", st.session_state.extracted_text, height=150)

        # Convert to speech button (separate, FIXED)
        if st.button("🎧 Convert Image Text to Speech"):
            if st.session_state.extracted_text.strip():
                audio_path = text_to_speech(st.session_state.extracted_text)
                audio_bytes = open(audio_path, "rb").read()
                st.audio(audio_bytes)
            else:
                st.warning("Extract text first")

# =========================
# FOOTER
# =========================
st.markdown("### 🚀 Built by Somya Jain")
