import streamlit as st
import whisper
from tempfile import NamedTemporaryFile
from pydub.utils import mediainfo
import re
from extract_video import BaseModel, AudioExtractModel
from main import process_video  # Added: import process_video
from summarize import summarize_text, save_summary_txt  # Added: Summarization functions
from noti import gmail_send_message  # Added: Gmail functionality for sending emails

# Initialize session state variables to persist data between Streamlit reruns
if 'transcription' not in st.session_state:
    st.session_state.transcription = None
if 'processed_file' not in st.session_state:
    st.session_state.processed_file = None
if 'email_recipients' not in st.session_state:
    st.session_state.email_recipients = []
if 'summary' not in st.session_state:
    st.session_state.summary = None

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

def video_to_audio_to_text(video_file):
    """
    Process video to extract audio and transcribe it to text using process_video from main.py.
    """
    with NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
        temp_file.write(video_file.read())
        temp_file_path = temp_file.name

    transcription = process_video(temp_file_path)  # Added: call process_video
    return transcription

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


def render_recipients():
    """
    Displays the list of email recipients along with remove buttons.
    """
    if st.session_state.email_recipients:
        st.markdown("### Recipients")
        for recipient in st.session_state.email_recipients:
            column_one, column_two = st.columns([4, 1])
            with column_one:
                st.markdown(f"<p style='color: #d8b4fe;'>{recipient}</p>", unsafe_allow_html=True)
            with column_two:
                if st.button("Remove", key=f"Remove {recipient}", help=f"Remove {recipient}"):  # add remove button
                    st.session_state.email_recipients.remove(recipient)
                    st.success(f"Removed {recipient} successfully.")
    else:
        st.write("No recipients added yet.")


def forstreamlit():
    """
    Main application function.
    """
    st.set_page_config(
        page_title="ECHOSCRIPT - Voice2Notes",
        page_icon="🎤",
        layout="centered"
    )
    
    setup_styles()
    render_header()

    st.markdown("""
        <p class="upload-text">Upload your audio file here:</p>
    """, unsafe_allow_html=True)

    video_file = st.file_uploader("", type=["mp4", "mp3", "wav"])

    if video_file is not None and video_file != st.session_state.processed_file:
        st.markdown(f"<p style='color: #d8b4fe; font-size: 1rem;'>Processing: {video_file.name}</p>", unsafe_allow_html=True)
        with st.spinner("Transcribing audio..."):
            transcription = video_to_audio_to_text(video_file)
            if transcription:
                st.session_state.transcription = transcription
                st.session_state.processed_file = video_file

    if st.session_state.transcription:
        st.markdown("<h3 style='color: #d8b4fe;'>Transcription Result</h3>", unsafe_allow_html=True)
        st.text_area("", value=st.session_state.transcription, height=200)

        # Summarize transcription
        st.markdown("<h3 style='color: #d8b4fe;'>Summary</h3>", unsafe_allow_html=True)
        summary = summarize_text(st.session_state.transcription)
        if summary:
            st.session_state.summary = summary
            st.text_area("Summary", value=summary, height=200)

            # Summary download
            st.download_button(
                label="Download Summary",
                data=summary,
                file_name="summary.txt",
                mime="text/plain"
            )

        # Email functionality
        handle_add_email_button()
        render_recipients()

        if st.session_state.email_recipients and "summary" in st.session_state:
            if st.button("Send Summary via Email"):
                for recipient in st.session_state.email_recipients:
                    with st.spinner(f"Sending email to {recipient}..."):
                        result = gmail_send_message(
                            to=recipient,
                            fro="your_email@gmail.com",
                            subject="Meeting Summary",
                            body=st.session_state.summary
                        )
                        if result:
                            st.success(f"Summary sent to {recipient}!")
                        else:
                            st.error(f"Failed to send email to {recipient}.")

if __name__ == "__main__":
    forstreamlit()
