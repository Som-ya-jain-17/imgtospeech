import streamlit as st
import azure.cognitiveservices.speech as speechsdk
import requests
import tempfile

# =========================
# 🔑 AZURE KEYS (YOUR PROVIDED KEYS)
# =========================
AZURE_SPEECH_KEY = "2LNcNfQUrK6f0jj3eZ1ssHm1qALaeiXmn1foajdEdGGo9bxH06i5JQQJ99CEACYeBjFXJ3w3AAAYACOGrjDr"
AZURE_SPEECH_REGION = "eastus"

AZURE_VISION_KEY = "3rjI2tJgEjvUS9ve9DnwGTdgu0JW5B5i0u2mE8QpRzgaCPh4l1AwJQQJ99CEACYeBjFXJ3w3AAAFACOG0FxE"
AZURE_VISION_ENDPOINT = "https://cv97898657.cognitiveservices.azure.com/vision/v3.2/ocr"

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="AI Image → Speech", layout="centered")

# =========================
# 🌈 PREMIUM UI
# =========================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#0b0f1a,#000814,#0b0f1a);
    color: white;
}

.title {
    text-align:center;
    font-size: 45px;
    font-weight: 900;
    background: linear-gradient(90deg,#ff00cc,#00ffff,#ffcc00,#8b5cf6);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}

.card {
    background: rgba(255,255,255,0.06);
    padding: 20px;
    border-radius: 18px;
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255,255,255,0.2);
}

.stButton>button {
    background: linear-gradient(90deg,#ff00cc,#00ffff,#8b5cf6);
    color:white;
    border-radius:10px;
    padding:10px 15px;
    border:none;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🖼️➡️📝➡️🎧 AI Image to Speech</div>', unsafe_allow_html=True)

# =========================
# STATE
# =========================
if "text_data" not in st.session_state:
    st.session_state.text_data = ""

# =========================
# VOICE
# =========================
voice = st.selectbox("🎤 Voice", ["en-US-JennyNeural", "en-IN-NeerjaNeural"])

# =========================
# IMAGE → TEXT (AZURE VISION)
# =========================
def image_to_text(image_bytes):
    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_VISION_KEY,
        "Content-Type": "application/octet-stream"
    }

    response = requests.post(AZURE_VISION_ENDPOINT, headers=headers, data=image_bytes)
    result = response.json()

    text = ""

    try:
        for region in result["regions"]:
            for line in region["lines"]:
                for word in line["words"]:
                    text += word["text"] + " "
                text += "\n"
    except:
        text = ""

    return text

# =========================
# TEXT → SPEECH (AZURE SPEECH)
# =========================
def text_to_speech(text):
    speech_config = speechsdk.SpeechConfig(
        subscription=AZURE_SPEECH_KEY,
        region=AZURE_SPEECH_REGION
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
# UI
# =========================
st.markdown('<div class="card">', unsafe_allow_html=True)

uploaded_file = st.file_uploader("📤 Upload Image", type=["png","jpg","jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Image")

    img_bytes = uploaded_file.read()

    if st.button("🔍 Extract Text from Image"):
        with st.spinner("Processing..."):
            st.session_state.text_data = image_to_text(img_bytes)

        if st.session_state.text_data.strip() == "":
            st.warning("No text detected")
        else:
            st.success("Text extracted successfully ✨")

st.text_area("📝 Extracted Text", st.session_state.text_data, height=150)

if st.button("🎧 Convert Text to Speech"):
    if st.session_state.text_data.strip() == "":
        st.warning("Extract text first")
    else:
        with st.spinner("Generating speech..."):
            audio = text_to_speech(st.session_state.text_data)

            audio_bytes = open(audio, "rb").read()
            st.audio(audio_bytes)

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("💎 Built with Azure AI | Image → Text → Speech")
