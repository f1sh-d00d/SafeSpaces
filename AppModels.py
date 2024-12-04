from langchain_community.llms import Ollama
import moviepy.editor as mp
import speech_recognition as sr
import librosa
import torch
import soundfile as sf
import sys
import wave
import json
import whisper
from urllib.request import urlopen, Request
import os
import base64
from email.message import EmailMessage
import numpy as np
import hashlib
import time
import hmac
import base64
import urllib.parse
import requests
from evernote.api.client import EvernoteClient
from evernote.edam.type.ttypes import Note, NoteAttributes
import oauth2

# Check if running on Apple Silicon
IS_ARM = torch.backends.mps.is_available()

class BaseModel:
    '''Generic Model Class'''
    def load(self):
        pass

    def run(self):
        pass


class AudioExtractModel(BaseModel):
    def __init__(self):
        self.audio_path = "meeting_audio.wav"
        self.video_path = None

    def load(self, video_path):
        '''sets model's video'''
        self.video_path = video_path

    def run(self):
        '''returns path to audio extracted from video with optimized processing'''
        video = mp.VideoFileClip(self.video_path)
        
        # Optimize audio extraction for M1/M2
        if IS_ARM:
            # Use more efficient audio processing on Apple Silicon
            audio_buffer = video.audio.to_soundarray(fps=16000, nbytes=2, quantize=True)
            audio_buffer = np.mean(audio_buffer, axis=1) if audio_buffer.ndim > 1 else audio_buffer
            sf.write(self.audio_path, audio_buffer, 16000)
        else:
            # Fall back to standard processing for other architectures
            video.audio.write_audiofile(self.audio_path)

        return self.audio_path


class TranscriptModel(BaseModel):
    def __init__(self):
        # Force CPU usage regardless of platform
        self.device = "cpu"
        self.model = whisper.load_model("base", device=self.device)

    def load(self, audio_path):
        self.audio_path = audio_path

    def run(self):
        # Remove device-specific optimizations
        result = self.model.transcribe(self.audio_path, fp16=False)
        return result['text']


class SummaryModel(BaseModel):
    def __init__(self):
        self.model = Ollama(
            base_url="http://localhost:11434",
            model="llama3.2"
        )
        self.notes_path = "MeetingNotes.txt"

    def load(self, transcript_text):
        self.text = transcript_text
    
    def run(self):
        # Optimize for M1/M2 by using Metal-optimized Ollama
        if IS_ARM:
            os.environ["OLLAMA_HOST"] = "http://localhost:11434"
            os.environ["METAL_DEVICE"] = "1"  # Enable Metal support
            
        prompt = f"Write a detailed summary this meeting:\n{self.text}"
        notes = self.model.invoke(prompt)
        
        with open(self.notes_path, "w") as fout:
            fout.write(notes)

        return self.notes_path





class EvernoteModel(BaseModel):
    def __init__(self):
        self.client = None
        self.note_store = None
        self.content = None
        self.title = None
        # Add your credentials here
        self.consumer_key = "key"
        self.consumer_secret = "secret"
        self.callback_url = "url"
        self.token_expiry = None
        
        # Test connection to Evernote
        try:
            test_client = EvernoteClient(
                consumer_key=self.consumer_key,
                consumer_secret=self.consumer_secret,
            )
            print("Successfully created test Evernote client")
        except Exception as e:
            print(f"Error testing Evernote connection: {str(e)}")

    def initialize_oauth(self):
        """Step 1: Generate a Temporary Token"""
        try:
            # Create OAuth client
            consumer = oauth2.Consumer(self.consumer_key, self.consumer_secret)
            client = oauth2.Client(consumer)
            
            # Use the correct Evernote API endpoints
            request_url =  'https://www.evernote.com/oauth'
            
            # Prepare the request parameters
            params = {
                'oauth_callback': self.callback_url,
                'oauth_consumer_key': self.consumer_key,
                'oauth_signature_method': 'HMAC-SHA1',
                'oauth_timestamp': str(int(time.time())),
                'oauth_nonce': oauth2.generate_nonce(),
                'oauth_version': '1.0'
            }
            
            # Generate the OAuth signature
            req = oauth2.Request(method='GET', url=request_url, parameters=params)
            signature_method = oauth2.SignatureMethod_HMAC_SHA1()
            req.sign_request(signature_method, consumer, None)
            
            # Make the request for a temporary token
            headers = req.to_header()
            resp, content = client.request(request_url, 'GET', headers=headers)
            
            if resp['status'] != '200':
                print(f"Failed to get temporary token. Status: {resp['status']}")
                print(f"Response content: {content}")
                return None
                
            request_token = dict(urllib.parse.parse_qsl(content.decode('utf-8')))
            print(f"Got request token: {request_token}")
            return request_token
            
        except Exception as e:
            print(f"OAuth Initialization Error: {str(e)}")
            return None

    def get_authorize_url(self, request_token):
        """Step 2: Request User Authorization"""
        if not request_token:
            return None
            
        base_url = 'https://www.evernote.com/oauth' 
        return f"{base_url}?oauth_token={request_token['oauth_token']}"

    def complete_oauth(self, request_token, oauth_verifier):
        """Step 3: Retrieve Access Token"""
        try:
            if not oauth_verifier:
                print("No OAuth verifier - user probably denied access")
                return None

            client = oauth2.Client(
                oauth2.Consumer(self.consumer_key, self.consumer_secret),
                oauth2.Token(
                    request_token['oauth_token'],
                    request_token.get('oauth_token_secret', '')
                )
            )

            request_url = 'https://www.evernote.com/oauth' 
            resp, content = client.request(
                request_url,
                'GET',
                body=urllib.parse.urlencode({'oauth_verifier': oauth_verifier})
            )

            if resp['status'] != '200':
                print(f"Failed to get access token: {content}")
                return None

            access_token = dict(urllib.parse.parse_qsl(content.decode('utf-8')))
            
            return {
                'access_token': access_token['oauth_token'],
                'expiry': int(access_token['edam_expires'])
            }
            
        except Exception as e:
            print(f"Error completing OAuth: {str(e)}")
            return None

    def is_token_expired(self, token_expiry):
        """Check if the token is expired"""
        if not token_expiry:
            return True
        current_time = int(time.time() * 1000)  # Convert to milliseconds
        return current_time >= token_expiry

    def refresh_token(self, refresh_token):
        """Refresh the access token"""
        try:
            client = EvernoteClient(
                consumer_key=self.consumer_key,
                consumer_secret=self.consumer_secret,
            )
            auth_result = client.refresh_access_token(refresh_token)
            
            if isinstance(auth_result, dict):
                access_token = auth_result.get('oauth_token')
                self.token_expiry = auth_result.get('edam_expires')
            else:
                access_token = auth_result
                self.token_expiry = int(time.time() * 1000) + (365 * 24 * 60 * 60 * 1000)
            
            return {
                'access_token': access_token,
                'expiry': self.token_expiry
            }
        except Exception as e:
            print(f"Error refreshing token: {str(e)}")
            return None

    def load(self, access_token, content, title="Meeting Notes"):
        """Initialize Evernote client with OAuth access token and set note content"""
        try:
            self.client = EvernoteClient(token=access_token)
            self.note_store = self.client.get_note_store()
            self.content = content
            self.title = title
            return True
        except Exception as e:
            print(f"Error loading Evernote client: {str(e)}")
            return False

    def run(self):
        """Create and upload note to Evernote"""
        try:
            if not self.client or not self.note_store:
                return None

            # Create note object
            note = Note()
            note.title = self.title
            
            # Create the note's content in ENML format
            note.content = '<?xml version="1.0" encoding="UTF-8"?>'
            note.content += '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
            note.content += '<en-note>'
            note.content += f'<div>{self.content}</div>'
            note.content += '</en-note>'

            # Create note in Evernote
            created_note = self.note_store.createNote(note)
            return created_note.guid
        except Exception as e:
            if 'AuthenticationException' in str(e) or 'EDAMUserException' in str(e):
                return 'TOKEN_EXPIRED'
            print(f"Error creating note: {str(e)}")
            return None
        
    def save_to_evernote():
        """Save transcription to Evernote"""
        if not st.session_state.get('evernote_access_token'):
            st.error("Please authenticate with Evernote first.")
            return

        evernote = st.session_state.evernote_instance
        evernote.token = st.session_state['evernote_access_token']

        content = st.session_state.transcription
        title = f"Meeting Notes - {time.strftime('%Y-%m-%d %H:%M')}"

        if evernote.load(content, title):
            note_guid = evernote.run()
            if note_guid:
                st.success("Successfully saved to Evernote!")
            else:
                st.error("Failed to save note to Evernote.")
        else:
            st.error("Failed to prepare note content.")

    def initialize_with_token(self, token):
        """Initialize Evernote client with developer token"""
        try:
            self.client = EvernoteClient(token=token)
            self.note_store = self.client.get_note_store()
            return True
        except Exception as e:
            print(f"Error initializing with token: {str(e)}")
            return False


def main():
    file_name = sys.argv[1]
    audio_model = AudioExtractModel()
    audio_model.load(file_name)
    audio_path = audio_model.run()

    transcriber = TranscriptModel()
    transcriber.load(audio_path)
    transcriber.run()

    summarizer = SummaryModel()
    summarizer.load("MathMeeting.txt")
    summarizer.run()


if __name__ == "__main__":
    main()

