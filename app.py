import streamlit as st
from tempfile import NamedTemporaryFile
from pydub.utils import mediainfo
import re
from AppModels import BaseModel, AudioExtractModel, TranscriptModel, SummaryModel, EvernoteModel
from evernote.api.client import EvernoteClient
from evernote.edam.type.ttypes import Note, NoteAttributes
import hashlib
import time
import oauth2

# Initialize session state variables to persist data between Streamlit reruns
if 'transcription' not in st.session_state:
    st.session_state.transcription = None
if 'processed_file' not in st.session_state:
    st.session_state.processed_file = None
if 'email_recipients' not in st.session_state:
    st.session_state.email_recipients = []
if 'transcription_path' not in st.session_state:
    st.session_state.transcription_path = ''
if 'evernote_token' not in st.session_state:
    st.session_state.evernote_token = None

# Initialize additional session state variables for OAuth
if 'evernote_request_token' not in st.session_state:
    st.session_state.evernote_request_token = None
if 'evernote_access_token' not in st.session_state:
    st.session_state.evernote_access_token = None
if 'evernote_token_expiry' not in st.session_state:
    st.session_state.evernote_token_expiry = None
if 'evernote_oauth_verifier' not in st.session_state:
    st.session_state.evernote_oauth_verifier = None

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
def video_to_audio_to_text(video_file):
    """
    Input video will extract the audio file for Whisper model to transcribe to text
    """

    with NamedTemporaryFile(suffix=".temp", delete=False) as temp_file:
        temp_file.write(video_file.read())
        temp_file_path = temp_file.name

    info = mediainfo(temp_file_path)
    input_format = info["format_name"] 

    if "mp4" in input_format or "mov" in input_format:
        audio_model = AudioExtractModel()
        audio_model.load(temp_file_path)
        audio_path = audio_model.run()
    else:
        audio_path = temp_file_path

    transcriber = TranscriptModel()
    transcriber.load(audio_path)
    transcription = transcriber.run()

    note_taker = SummaryModel()
    note_taker.load(transcription)
    note_file_path = note_taker.run()

    return note_file_path

        
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




def handle_evernote_auth():
    """Handle Evernote OAuth authentication"""
    if 'evernote_instance' not in st.session_state:
        st.session_state.evernote_instance = EvernoteModel()

    evernote = st.session_state.evernote_instance

    if not st.session_state.get('evernote_access_token'):
        st.markdown("<h4 style='color: #d8b4fe;'>Evernote Authentication</h4>", unsafe_allow_html=True)
        
        if st.button("Start OAuth Flow"):
            # Step 1: Get temporary token
            request_token = evernote.initialize_oauth()
            
            if request_token and 'oauth_token' in request_token:
                # Store request token in session
                st.session_state['evernote_request_token'] = request_token
                # Step 2: Get authorization URL
                auth_url = evernote.get_authorize_url(request_token)
                st.markdown("### Authorization Steps:")
                st.markdown("1. Click the link below to authorize the application")
                st.markdown("2. After authorization, you'll be redirected back to this page")
                st.markdown(f"[Click here to authorize with Evernote]({auth_url})")
            else:
                st.error("Failed to start OAuth flow. Please check your credentials.")

    # Handle OAuth callback
    params = st.query_params
    if 'oauth_verifier' in params and 'evernote_request_token' in st.session_state:
        oauth_verifier = params['oauth_verifier']
        request_token = st.session_state['evernote_request_token']
        
        # Step 3: Get access token
        auth_result = evernote.complete_oauth(request_token, oauth_verifier)
        if auth_result and 'access_token' in auth_result:
            st.session_state['evernote_access_token'] = auth_result['access_token']
            st.session_state['evernote_token_expiry'] = auth_result['expiry']
            st.success("Successfully authenticated with Evernote!")
            st.experimental_rerun()
        else:
            st.error("Failed to complete OAuth flow. Please try again.")

def save_to_evernote():
    """Save transcription to Evernote using OAuth"""
    evernote = EvernoteModel()
    
    if not st.session_state.evernote_access_token:
        st.error("Please complete Evernote OAuth authentication first.")
        return
        
    if evernote.is_token_expired(st.session_state.evernote_token_expiry):
        # Try to refresh the token
        refresh_result = evernote.refresh_token(st.session_state.evernote_access_token)
        if refresh_result:
            st.session_state.evernote_access_token = refresh_result['access_token']
            st.session_state.evernote_token_expiry = refresh_result['expiry']
        else:
            st.error("Your Evernote session has expired. Please authenticate again.")
            st.session_state.evernote_access_token = None
            st.session_state.evernote_token_expiry = None
            st.experimental_rerun()
            return
    
    title = f"Meeting Notes - {time.strftime('%Y-%m-%d %H:%M')}"
    if evernote.load(st.session_state.evernote_access_token, st.session_state.transcription, title):
        note_guid = evernote.run()
        if note_guid == 'TOKEN_EXPIRED':
            st.error("Your Evernote session has expired. Please authenticate again.")
            st.session_state.evernote_access_token = None
            st.session_state.evernote_token_expiry = None
            st.experimental_rerun()
        elif note_guid:
            st.success("Successfully saved to Evernote!")
        else:
            st.error("Failed to save to Evernote. Please try again.")
    else:
        st.error("Failed to initialize Evernote client. Please try authenticating again.")

def main():
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

    video_file = st.file_uploader("", type=[".mov", ".mp4", "mp3", "wav"])

    if video_file is not None and video_file != st.session_state.processed_file:
        st.markdown(f"<p style='color: #d8b4fe; font-size: 1rem;'>Processing: {video_file.name}</p>", unsafe_allow_html=True)
        transcription_path = None
        with st.spinner("Transcribing audio..."):
            st.session_state.transcription_path = video_to_audio_to_text(video_file)
            with open(st.session_state.transcription_path, "r") as file:
                transcription = file.read()
            if transcription:
                st.session_state.transcription = transcription
                st.session_state.processed_file = video_file

    if st.session_state.transcription:
        st.markdown("<h3 style='color: #d8b4fe; font-size: 1.25rem; margin-top: 2rem;'>Transcription Result</h3>", unsafe_allow_html=True)
        st.text_area("", value=st.session_state.transcription, height=200)

        column_one, column_two, column_three = st.columns(3)
        with column_one:
            st.download_button(
                label="Download the Summary",
                data=st.session_state.transcription,
                file_name=f"transcript_{st.session_state.processed_file.name}.txt",
                mime="text/plain",
                key="fullScriptDownloadButton"
            )
        
        with column_two:
            if st.button("Save to Evernote"):
                save_to_evernote()
        
        handle_add_email_button()
        render_recipients()

        with column_three:
            if st.session_state.email_recipients:
                if st.button("Email the Summary"):
                    send_email_transcript()
            else:
                st.write("Please add recipients to email the summary.")

        # Add Evernote authentication section
        st.markdown("---")
        st.markdown("<h3 style='color: #d8b4fe; font-size: 1.25rem;'>Evernote Settings</h3>", unsafe_allow_html=True)
        handle_evernote_auth()

if __name__ == "__main__":
    main()
