import streamlit as st
import azure.cognitiveservices.speech as speechsdk
import tempfile

# =========================
# CONFIG (USE YOUR KEY)
# =========================
SPEECH_KEY = "2LNcNfQUrK6f0jj3eZ1ssHm1qALaeiXmn1foajdEdGGo9bxH06i5JQQJ99CEACYeBjFXJ3w3AAAYACOGrjDr"
SPEECH_REGION = "eastus"

st.set_page_config(page_title="AI Speech Studio", layout="centered")

# =========================
# SAFE DARK UI (NO BREAK)
# =========================
st.markdown("""
<style>
.stApp {
    background-color: #0b0f1a;
    color: white;
}
h1 {
    text-align: center;
    color: #8b5cf6;
}
</style>
""", unsafe_allow_html=True)

st.title("🎧 AI Text → Speech Studio")

# =========================
# SIDEBAR
# =========================
voice = st.sidebar.selectbox(
    "Select Voice",
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

    result = synthesizer.speak_text_async(text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        return audio_file
    else:
        return None

# =========================
# TEXT SECTION
# =========================
st.subheader("✍️ Text to Speech")

text_input = st.text_area("Enter text")

if st.button("Generate Speech"):
    if text_input.strip() == "":
        st.warning("Please enter text")
    else:
        audio_path = text_to_speech(text_input)

        if audio_path:
            audio_bytes = open(audio_path, "rb").read()
            st.audio(audio_bytes)
        else:
            st.error("Speech generation failed")

# =========================
# IMAGE SECTION (SAFE VERSION)
# =========================
st.subheader("🖼️ Image Upload (Preview Only)")

uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Image")

    st.info("💡 Image uploaded successfully. (OCR removed to prevent errors)")

# =========================
# FOOTER
# =========================
st.markdown("---")
st.markdown("🚀 Built by Somya Jain")
