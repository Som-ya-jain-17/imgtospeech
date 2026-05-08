import streamlit as st
import azure.cognitiveservices.speech as speechsdk
import requests
import tempfile

# =========================
# 🔑 AZURE SPEECH (YOUR KEY)
# =========================
AZURE_SPEECH_KEY = "2LNcNfQUrK6f0jj3eZ1ssHm1qALaeiXmn1foajdEdGGo9bxH06i5JQQJ99CEACYeBjFXJ3w3AAAYACOGrjDr"
AZURE_SPEECH_REGION = "eastus"

# ⚠️ YOU MUST ADD VISION KEY HERE (required for image → text)
AZURE_VISION_KEY = "YOUR_VISION_KEY_HERE"
AZURE_VISION_ENDPOINT = "https://eastus.api.cognitive.microsoft.com/vision/v3.2/ocr"

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="AI Image Speech Studio", layout="centered")

# =========================
# ✨ PREMIUM GLASS + NEON UI
# =========================
st.markdown("""
<style>

.stApp {
    background: radial-gradient(circle at top, #0b0f1a, #000814, #0b0f1a);
    color: white;
}

/* TITLE */
.title {
    text-align: center;
    font-size: 52px;
    font-weight: 900;
    background: linear-gradient(90deg,#ff00cc,#00ffff,#ffcc00,#8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: glow 2s infinite alternate;
}

@keyframes glow {
    from {filter: drop-shadow(0 0 10px #ff00cc);}
    to {filter: drop-shadow(0 0 25px #00ffff);}
}

/* CARD */
.card {
    background: rgba(255,255,255,0.05);
    padding: 25px;
    border-radius: 20px;
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.2);
    box-shadow: 0 0 30px rgba(0,255,255,0.15);
}

/* BUTTON */
.stButton>button {
    background: linear-gradient(90deg,#ff00cc,#00ffff,#8b5cf6);
    color: white;
    border-radius: 12px;
    padding: 10px 18px;
    border: none;
    font-weight: bold;
    box-shadow: 0 0 20px rgba(0,255,255,0.4);
    transition: 0.3s;
}

.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 35px rgba(255,0,255,0.6);
}

/* TEXT AREA */
textarea {
    background-color: #0b0f1a !important;
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

# =========================
# TITLE
# =========================
st.markdown('<div class="title">✨ AI Image → Speech Studio ✨</div>', unsafe_allow_html=True)

# =========================
# SESSION STATE
# =========================
if "text_data" not in st.session_state:
    st.session_state.text_data = ""

# =========================
# VOICE
# =========================
voice = st.selectbox("🎤 Choose Voice", ["en-US-JennyNeural", "en-IN-NeerjaNeural"])

# =========================
# IMAGE → TEXT (AZURE OCR)
# =========================
def extract_text(image_bytes):
    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_VISION_KEY,
        "Content-Type": "application/octet-stream"
    }

    response = requests.post(AZURE_VISION_ENDPOINT, headers=headers, data=image_bytes)
    data = response.json()

    text = ""

    try:
        for region in data["regions"]:
            for line in region["lines"]:
                for word in line["words"]:
                    text += word["text"] + " "
                text += "\n"
    except:
        text = ""

    return text

# =========================
# TEXT → SPEECH
# =========================
def speak_text(text):
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
# UI CONTAINER
# =========================
st.markdown('<div class="card">', unsafe_allow_html=True)

uploaded_file = st.file_uploader("📤 Upload Image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Image")

    img_bytes = uploaded_file.read()

    if st.button("🔍 Extract Text"):
        with st.spinner("Extracting text..."):
            st.session_state.text_data = extract_text(img_bytes)

        if st.session_state.text_data.strip() == "":
            st.warning("No text detected 😕")
        else:
            st.success("Text extracted successfully ✨")

st.text_area("📝 Extracted Text", st.session_state.text_data, height=150)

if st.button("🎧 Convert to Speech"):
    if st.session_state.text_data.strip() == "":
        st.warning("Please extract text first")
    else:
        with st.spinner("Generating speech..."):
            audio = speak_text(st.session_state.text_data)
            audio_bytes = open(audio, "rb").read()
            st.audio(audio_bytes)

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# FOOTER
# =========================
st.markdown("💎 Built with Azure AI • Somya Jain")
