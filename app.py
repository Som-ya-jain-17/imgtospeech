import streamlit as st
import requests
import time
import azure.cognitiveservices.speech as speechsdk
from PIL import Image
import tempfile
import os

# ---------------------------
# AZURE SPEECH (YOUR KEY)
# ---------------------------
SPEECH_KEY = "2LNcNfQUrK6f0jj3eZ1ssHm1qALaeiXmn1foajdEdGGo9bxH06i5JQQJ99CEACYeBjFXJ3w3AAAYACOGrjDr"
SPEECH_REGION = "eastus"

# ---------------------------
# AZURE VISION (PUT YOUR KEYS HERE)
# ---------------------------
VISION_KEY = "3rjI2tJgEjvUS9ve9DnwGTdgu0JW5B5i0u2mE8QpRzgaCPh4l1AwJQQJ99CEACYeBjFXJ3w3AAAFACOG0FxE"
VISION_ENDPOINT = " https://cv97898657.cognitiveservices.azure.com/"

# ---------------------------
# STREAMLIT UI
# ---------------------------
st.set_page_config(page_title="AI Vision Speech Studio", page_icon="🎙️", layout="centered")

st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top, #0f172a, #050816, #000000);
    color: white;
}

.title {
    text-align: center;
    font-size: 42px;
    font-weight: 900;
    background: linear-gradient(90deg, #00f5ff, #a855f7, #ff00cc, #00ff88);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.stButton>button {
    background: linear-gradient(135deg, #00f5ff, #7c3aed, #ff00cc);
    color: white;
    border-radius: 14px;
    padding: 0.6rem 1.2rem;
    font-weight: bold;
    border: none;
    box-shadow: 0 0 20px rgba(0,255,255,0.3);
}

.stButton>button:hover {
    transform: scale(1.05);
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🎙️ AI Vision Speech Studio</div>', unsafe_allow_html=True)

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
# 🔥 AZURE VISION OCR FUNCTION
# ---------------------------
def extract_text_vision(image_file):
    read_url = VISION_ENDPOINT + "vision/v3.2/read/analyze"

    headers = {
        "Ocp-Apim-Subscription-Key": VISION_KEY,
        "Content-Type": "application/octet-stream"
    }

    image_data = image_file.getvalue()

    response = requests.post(read_url, headers=headers, data=image_data)

    if response.status_code != 202:
        return "Error in Vision API"

    operation_url = response.headers["Operation-Location"]

    # Polling result
    while True:
        result = requests.get(operation_url, headers={
            "Ocp-Apim-Subscription-Key": VISION_KEY
        })

        analysis = result.json()

        if "analyzeResult" in analysis:
            break

        if analysis.get("status") == "failed":
            return "OCR Failed"

        time.sleep(1)

    text = ""
    for line in analysis["analyzeResult"]["readResults"][0]["lines"]:
        text += line["text"] + "\n"

    return text

# ---------------------------
# UI
# ---------------------------
tab1, tab2 = st.tabs(["📝 Text to Speech", "🖼️ Image to Speech"])

with tab1:
    text = st.text_area("Enter text")
    if st.button("Speak Text"):
        if text.strip():
            audio = text_to_speech(text)
            st.audio(audio)

with tab2:
    file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

    if file:
        st.image(file, caption="Uploaded Image")

        if st.button("Extract Text (AI Vision)"):
            extracted = extract_text_vision(file)

            st.success("Extracted Text")
            st.write(extracted)

            if extracted.strip():
                audio = text_to_speech(extracted)
                st.audio(audio)
