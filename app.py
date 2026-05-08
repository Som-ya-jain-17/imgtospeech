import streamlit as st
import azure.cognitiveservices.speech as speechsdk
from PIL import Image
import pytesseract
import tempfile

# ---------------------------
# Azure Configuration
# ---------------------------
SPEECH_KEY = "YOUR_AZURE_SPEECH_KEY"
SPEECH_REGION = "YOUR_REGION"

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(page_title="AI Speech App", page_icon="🎙️", layout="centered")

st.markdown(
    """
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .title {
        text-align: center;
        font-size: 40px;
        font-weight: bold;
        color: #4A90E2;
    }
    .footer {
        text-align: center;
        margin-top: 50px;
        font-size: 14px;
        color: gray;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="title">🎙️ AI Image & Text to Speech</div>', unsafe_allow_html=True)
st.write("Convert text or image content into speech easily!")

# ---------------------------
# Function: Text to Speech
# ---------------------------
def text_to_speech(text):
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    speech_config.speech_synthesis_voice_name = "en-IN-NeerjaNeural"

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        audio_filename = tmp_file.name

    audio_config = speechsdk.audio.AudioOutputConfig(filename=audio_filename)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    synthesizer.speak_text_async(text).get()
    return audio_filename

# ---------------------------
# Tabs
# ---------------------------
tab1, tab2 = st.tabs(["📝 Text to Speech", "🖼️ Image to Speech"])

# ---------------------------
# Tab 1: Text to Speech
# ---------------------------
with tab1:
    st.subheader("Enter Text")
    user_text = st.text_area("Type something...", height=150)

    if st.button("🔊 Convert to Speech"):
        if user_text.strip() == "":
            st.warning("Please enter some text.")
        else:
            audio_file = text_to_speech(user_text)
            st.audio(audio_file)

# ---------------------------
# Tab 2: Image to Speech
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
