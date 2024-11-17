import streamlit as st
import whisper
from tempfile import NamedTemporaryFile
from io import BytesIO
from pydub.utils import mediainfo
import re

# Initialize session state variables to persist data between Streamlit reruns
if 'transcription' not in st.session_state:
    st.session_state.transcription = None
if 'processed_file' not in st.session_state:
    st.session_state.processed_file = None
if 'email_recipients' not in st.session_state:
    st.session_state.email_recipients = []

def setup_styles():
    """
    Configure page styling using custom CSS.
    """
    st.markdown("""
        <style>
        .stApp, .main, .element-container, .block-container, div[data-testid="stToolbar"],
        div[data-testid="stDecoration"], div[data-testid="stStatusWidget"] {
            background-color: #000000 !important;
        }
        .gradient-text {
            background: linear-gradient(90deg, #a78bfa 0%, #ec4899 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .stButton>button {
            background-color: #7e22ce;
            color: white;
            width: 100%;
            padding: 0.75rem;
            border-radius: 0.5rem;
            transition: background-color 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #cd72f7;
            transform: translateY(-1px);
        }
        .local-processing-text {
            color: #a78bfa;
            font-size: 1.25rem;
            font-weight: bold;
        }
        .upload-text {
            color: white;
            font-size: 1.25rem;
            font-weight: bold;
            padding: 10px;
        }
        a {
            color: #d8b4fe !important;
            text-decoration: none !important;
        }
        .element-container div[data-testid="stMarkdownContainer"] p {
            color: #d8b4fe !important;
        }
                
        .existingEmail{                
            background-color:rgb(133, 33, 3, 0.5); 
            padding:10px; 
            border-radius:5px;
        }
            
        </style>
    """, unsafe_allow_html=True)


def render_header():
    """
    Renders the application header with logo and processing message.
    """
    _, column_two, _ = st.columns([1, 2, 1])
    with column_two:
        st.image("logoblack.PNG", use_container_width=True)
        st.markdown("""
            <div style='text-align: center; margin-top: -20px;'>
                <p class='local-processing-text'>100% Local Processing</p>
            </div>
        """, unsafe_allow_html=True)


@st.cache_resource
def load_whisper_model():
    """
    Loads and caches the Whisper speech recognition model.
    """
    return whisper.load_model("base")


def speech_to_text(audio_file):
    """
    Converts speech in the audio file to text using the Whisper model.
    """
    model = whisper.load_model("base")
    input_audio = audio_file.read()

    with NamedTemporaryFile(suffix=".tmp", delete=False) as temp_file:
        temp_file.write(input_audio)
        temp_file_path = temp_file.name

    info = mediainfo(temp_file_path)
    audio_format = info["format_name"]

    if "mp3" in audio_format:
        suffix = ".mp3"
    elif "wav" in audio_format:
        suffix = ".wav"
    else:
        raise ValueError(f"{audio_format} is an unsupported audio format")

    result = model.transcribe(temp_file_path, fp16=False)
    return result['text']


def handle_add_email_button():
    """
    Manages the email recipient addition functionality.
    """
    email = st.text_input("Enter an email address")
    if st.button("Add", key="add_email_button", help="Add email to recipients"):
        if re.match(r"[^@]+@[^@]+\.[^@]+", email):
            if email not in st.session_state.email_recipients:
                st.session_state.email_recipients.append(email)
                st.success(f"Added {email} to recipients list.")
            else: 
                st.markdown(f"""<div class= "existingEmail"> {email} has already been added to the recipients list</div>""", unsafe_allow_html=True)
        else:
            st.error("Please enter a valid email address.")


def handle_remove_email_button(email):
    """Manage deletion of emails already add to the recepient list"""
    st.session_state.email_recipients.remove(email)
    st.success(f"Are you sure? If so, click 'Remove' again")
 

def render_recipients():
    """
    Displays the list of email recipients along with remove buttons.
    """
    if st.session_state.email_recipients:
        st.markdown("### Recipients")
        for recipient in st.session_state.email_recipients:
            column_one, column_two= st.columns([4,1])
            with column_one:
                st.markdown(f"<p style='color: #d8b4fe;'>{recipient}</p>", unsafe_allow_html=True)
            with column_two:
                if st.button("Remove", key=f"Remove {recipient}", help=f"Remove {recipient}"): #add remove button
                    handle_remove_email_button(recipient)
    else:
        st.write("No recipients added yet.")



def send_email_transcript():
    """
    Simulates sending the transcript via email.
    """
    if not st.session_state.email_recipients:
        st.error("No recipients added. Please add at least one email.")
        return

    st.success(f"Sent the transcript to {', '.join(st.session_state.email_recipients)}")

def forstreamlit():
    """
    Main application function.
    """
    st.set_page_config(
        page_title="ECHOSCRIPT - Voice2Notes",
        page_icon="ðŸŽ¤",
        layout="centered"
    )
    
    setup_styles()
    render_header()

    st.markdown("""
        <p class="upload-text">Upload your audio file here:</p>
    """, unsafe_allow_html=True)

    audio_file = st.file_uploader("", type=["mp3", "wav"])

    if audio_file is not None and audio_file != st.session_state.processed_file:
        st.markdown(f"<p style='color: #d8b4fe; font-size: 1rem;'>Processing: {audio_file.name}</p>", unsafe_allow_html=True)
        with st.spinner("Transcribing audio..."):
            transcription = speech_to_text(audio_file)
            if transcription:
                st.session_state.transcription = transcription
                st.session_state.processed_file = audio_file

    if st.session_state.transcription:
        st.markdown("<h3 style='color: #d8b4fe; font-size: 1.25rem; margin-top: 2rem;'>Transcription Result</h3>", unsafe_allow_html=True)
        st.text_area("", value=st.session_state.transcription, height=200)

        column_one, column_two = st.columns(2)
        with column_one:
            st.download_button(
                label="Download the Summary",
                data=st.session_state.transcription,
                file_name=f"transcript_{st.session_state.processed_file.name}.txt",
                mime="text/plain",
                key="fullScriptDownloadButton"
            )
        
        handle_add_email_button()
        render_recipients()

        with column_two:
            if st.session_state.email_recipients:
                if st.button("Email the Summary"):
                    send_email_transcript()
            else:
                st.write("Please add recipients to email the summary.")
        
            

if __name__ == "__main__":
    forstreamlit()
