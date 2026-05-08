import streamlit as st
import azure.cognitiveservices.speech as speechsdk
import requests
import tempfile

# =========================
# 🔑 AZURE KEYS (YOUR SAME KEYS)
# =========================
AZURE_SPEECH_KEY = "2LNcNfQUrK6f0jj3eZ1ssHm1qALaeiXmn1foajdEdGGo9bxH06i5JQQJ99CEACYeBjFXJ3w3AAAYACOGrjDr"
AZURE_SPEECH_REGION = "eastus"

AZURE_VISION_KEY = "3rjI2tJgEjvUS9ve9DnwGTdgu0JW5B5i0u2mE8QpRzgaCPh4l1AwJQQJ99CEACYeBjFXJ3w3AAAFACOG0FxE"
AZURE_VISION_ENDPOINT = "https://cv97898657.cognitiveservices.azure.com/vision/v3.2/ocr"

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="AI Vision Speech Studio", layout="centered")

# =========================
# 🌫️ CLASSY GLASS UI (NO BRIGHT COLORS)
# =========================
st.markdown("""
<style>

/* SOFT DARK BACKGROUND */
.stApp {
    background: #0b0f14;
    color: #e6e6e6;
    font-family: "Segoe UI";
}

/* TITLE */
.title {
    text-align:center;
    font-size: 38px;
    font-weight: 600;
    color: #eaeaea;
    letter-spacing: 1px;
    margin-bottom: 10px;
}

/* GLASS CARD */
.card {
    background: rgba(255,255,255,0.04);
    padding: 22px;
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(18px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.4);
}

/* SOFT BUTTON */
.stButton>button {
    background: rgba(255,255,255,0.08);
    color: #f1f1f1;
    border-radius: 10px;
    padding: 10px 16px;
    border: 1px solid rgba(255,255,255,0.1);
    transition: all 0.2s ease-in-out;
}

/* HOVER EFFECT */
.stButton>button:hover {
    background: rgba(255,255,255,0.15);
    transform: scale(1.02);
    box-shadow: 0 0 12px rgba(255,255,255,0.08);
}

/* CLICK EFFECT */
.stButton>button:active {
    transform: scale(0.98);
    box-shadow: 0 0 5px rgba(255,255,255,0.05);
}

/* TEXT AREA */
textarea {
    background-color: #111820 !important;
    color: #eaeaea !important;
    border-radius: 10px !important;
}

</style>
""", unsafe_allow_html=True)

# =========================
# TITLE
# =========================
st.markdown('<div class="title">AI Image → Text → Speech</div>', unsafe_allow_html=True)

# =========================
# SESSION STATE
# =========================
if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = ""

# =========================
# VOICE SELECT
# =========================
voice = st.selectbox("Voice", ["en-US-JennyNeural", "en-IN-NeerjaNeural"])

# =========================
# IMAGE → TEXT
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
def speak(text):
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
# UI CARD
# =========================
st.markdown('<div class="card">', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload Image", type=["png","jpg","jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

    img_bytes = uploaded_file.read()

    if st.button("Extract Text"):
        with st.spinner("Reading image..."):
            st.session_state.extracted_text = extract_text(img_bytes)

# SHOW TEXT ALWAYS
st.text_area("Extracted Text", st.session_state.extracted_text, height=140)

# SPEECH BUTTON
if st.button("Convert to Speech"):
    if st.session_state.extracted_text.strip() == "":
        st.warning("Please extract text first")
    else:
        with st.spinner("Generating voice..."):
            audio = speak(st.session_state.extracted_text)
            audio_bytes = open(audio, "rb").read()
            st.audio(audio_bytes)

st.markdown('</div>', unsafe_allow_html=True)

# FOOTER
st.markdown("<div style='text-align:center;color:#777;margin-top:20px;'>Built with Azure AI</div>", unsafe_allow_html=True)
