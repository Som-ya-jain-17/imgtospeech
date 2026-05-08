import streamlit as st
import azure.cognitiveservices.speech as speechsdk
from PIL import Image
import pytesseract
import tempfile

# ---------------------------
# Azure Configuration (YOUR ORIGINAL KEYS)
# ---------------------------
SPEECH_KEY = "2LNcNfQUrK6f0jj3eZ1ssHm1qALaeiXmn1foajdEdGGo9bxH06i5JQQJ99CEACYeBjFXJ3w3AAAYACOGrjDr"
SPEECH_REGION = "eastus"
ENDPOINT = "https://eastus.api.cognitive.microsoft.com/"

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(page_title="AI Speech App", page_icon="🎙️", layout="centered")

# ---------------------------
# UI Styling
# ---------------------------
st.markdown("""
<style>
body {
    background-color: #f4f6f9;
}
.title {
    text-align: center;
    font-size: 38px;
    font-weight: bold;
    color: #2C3E50;
}
.footer {
    text-align: center;
    margin-top: 40px;
    font-size: 14px;
    color: gray;
}
.stButton>button {
    background-color: #4A90E2;
    color: white;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🎙️ AI Image & Text to Speech</div>', unsafe_allow_html=True)
st.write("Convert text or image content into speech using Azure AI 🚀")

# ---------------------------
# Function: Text to Speech
# ---------------------------
def text_to_speech(text):
    speech_config = speechsdk.SpeechConfig(
        subscription=SPEECH_KEY,
        region=SPEECH_REGION
    )

    speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        audio_filename = tmp_file.name

    audio_config = speechsdk.audio.AudioOutputConfig(filename=audio_filename)

    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    synthesizer.speak_text_async(text).get()

    return audio_filename

# ---------------------------
# Tabs
# ---------------------------
tab1, tab2 = st.tabs(["📝 Text to Speech", "🖼️ Image to Speech"])

# ---------------------------
# Text to Speech
# ---------------------------
with tab1:
    st.subheader("Enter Text")
    user_text = st.text_area("Type your text here...", height=150)

    if st.button("🔊 Convert to Speech"):
        if user_text.strip() == "":
            st.warning("Please enter some text.")
        else:
            audio_file = text_to_speech(user_text)
            st.audio(audio_file)

# ---------------------------
# Image to Speech
# ---------------------------
with tab2:
    st.subheader("Upload Image")
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        if st.button("🔍 Extract & Speak"):
            extracted_text = pytesseract.image_to_string(image)

            if extracted_text.strip() == "":
                st.error("No text found in image.")
            else:
                st.success("Extracted Text:")
                st.write(extracted_text)

                audio_file = text_to_speech(extracted_text)
                st.audio(audio_file)

# ---------------------------
# Footer
# ---------------------------
st.markdown('<div class="footer">✨ Developed by Somya Jain</div>', unsafe_allow_html=True)
