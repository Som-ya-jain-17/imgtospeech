import streamlit as st
import azure.cognitiveservices.speech as speechsdk
import pytesseract
from PIL import Image
import tempfile
import os

# =========================
# CONFIG
# =========================
SPEECH_KEY = "2LNcNfQUrK6f0jj3eZ1ssHm1qALaeiXmn1foajdEdGGo9bxH06i5JQQJ99CEACYeBjFXJ3w3AAAYACOGrjDr"
SPEECH_REGION = "eastus"

# FIX FOR STREAMLIT CLOUD
if os.path.exists("/usr/bin/tesseract"):
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

st.set_page_config(page_title="AI Speech Studio", layout="wide")

st.title("🎧 AI Text & Image → Speech")

# =========================
# SESSION STATE
# =========================
if "text_data" not in st.session_state:
    st.session_state.text_data = ""

# =========================
# SIDEBAR
# =========================
voice = st.sidebar.selectbox(
    "Select Voice",
    ["en-US-JennyNeural", "en-IN-NeerjaNeural"]
)

# =========================
# SPEECH FUNCTION
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

    result = synthesizer.speak_text_async(text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        return audio_file
    else:
        st.error("❌ Speech generation failed")
        return None

# =========================
# TABS
# =========================
tab1, tab2 = st.tabs(["✍️ Text Input", "🖼️ Image Upload"])

# -------- TEXT TAB --------
with tab1:
    text_input = st.text_area("Enter text here")

    if st.button("🚀 Convert Text to Speech"):
        if text_input.strip() == "":
            st.warning("Enter text first")
        else:
            audio_path = text_to_speech(text_input)

            if audio_path:
                audio_bytes = open(audio_path, "rb").read()
                st.audio(audio_bytes)

# -------- IMAGE TAB --------
with tab2:
    uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image")

        # Extract Text
        if st.button("🔍 Extract Text"):
            try:
                text = pytesseract.image_to_string(image)

                if text.strip() == "":
                    st.warning("⚠️ No text detected in image")
                else:
                    st.session_state.text_data = text
                    st.success("✅ Text Extracted!")

            except Exception as e:
                st.error(f"OCR Error: {e}")

        # Show extracted text ALWAYS
        st.text_area("Extracted Text", st.session_state.text_data, height=150)

        # Convert to speech
        if st.button("🎧 Convert to Speech"):
            if st.session_state.text_data.strip() == "":
                st.warning("Extract text first")
            else:
                audio_path = text_to_speech(st.session_state.text_data)

                if audio_path:
                    audio_bytes = open(audio_path, "rb").read()
                    st.audio(audio_bytes)

# =========================
# DEBUG (REMOVE LATER)
# =========================
with st.expander("⚙️ Debug Info"):
    st.write("Tesseract Path:", pytesseract.pytesseract.tesseract_cmd)
    st.write("Tesseract Exists:", os.path.exists("/usr/bin/tesseract"))
