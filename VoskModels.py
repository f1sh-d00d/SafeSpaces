from langchain_community.llms import Ollama
from vosk import Model, KaldiRecognizer
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
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request as Requesting
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


class BaseModel:
    '''Generic Model Class'''
    def load(self):
        pass

    def run(self):
        pass


class AudioExtractModel(BaseModel):
    def __init__(self):
        self.audio_path = "meeting_audio.wav"
        self.viedo_path = None

    def load(self, video_path):
        '''sets model's video'''
        self.video_path = video_path

    def run(self):
        '''returns path to audio extracted from video'''
        video = mp.VideoFileClip(self.video_path)              #extract audio
        video.audio.write_audiofile(self.audio_path)           #write extracted audio to file found at path

        #convert to mono audio
        audio, sr = librosa.load(self.audio_path, mono=True, sr=None)
        sf.write(self.audio_path, audio, sr)

        return self.audio_path                              #return path


class TranscriptModel(BaseModel):
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.model_path = "vosk-model-small-en-us-0.15"
        self.transcript_path = "MeetingText.txt"

    def load(self, audio_path):
        self.audio_path = audio_path

    def run(self):
        model = Model(self.model_path)                      #initialize Vosk model
        fin = wave.open(self.audio_path, "rb")
        rate = fin.getframerate()
        print(f"Sample Rate: {rate}")

        recognizer = KaldiRecognizer(model, rate)           #create audio recognizer from model, with file's sample rate

        print("Starting Transcription...")
        with open(self.transcript_path, "w") as fout:
            while True:
                data = fin.readframes(2000)                     #listen to audio in chuncks to get full audio
                if len(data) == 0:
                    break                                     #exit loop if there is no more audio
                if recognizer.AcceptWaveform(data):
                    result = recognizer.Result()
                    text = json.loads(result)["text"]
                    print(f"TEXT {text}")
                    fout.write(f"{text}\n")

        return self.transcript_path


class SummaryModel(BaseModel):
    def __init__(self):
        self.model = Ollama(
                base_url = "http://localhost:11434",
                model = "llama3.2")
        self.notes_path = "MeetingNotes.txt"

    def load(self, transcript_path):
        '''Get the text from the transcription file. Set it as text that will be passed to llama3.2 for summarization'''
        with open(transcript_path) as fin:
            self.text = fin.read()
    
    def run(self):
        prompt = f"Use only gender-neutral pronouns. Write a detailed summary this meeting:\n{self.text}"

        notes = self.model.invoke(prompt)
        with open(self.notes_path, "w") as fout:
            fout.write(notes)

        return self.notes_path


class EmailModel(BaseModel):
  def __init__(self):
    self.emailList = None
    self.notePath = None
    self.creds = None
    self.subject = None
    self.messageBody = None
    self.SCOPES = ["https://www.googleapis.com/auth/gmail.readonly","https://www.googleapis.com/auth/gmail.send","https://mail.google.com/","https://www.googleapis.com/auth/gmail.modify","https://www.googleapis.com/auth/gmail.compose"]



    if os.path.exists("token.json"):
      self.creds = Credentials.from_authorized_user_file("token.json", self.SCOPES)
    if not self.creds or not self.creds.valid:
      if self.creds and self.creds.expired and self.creds.refresh_token:
        flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", self.SCOPES
        )
        self.creds = flow.run_local_server(port=0)
      else:
        flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", self.SCOPES
        )
        self.creds = flow.run_local_server(port=0)
      # Save the credentials for the next run
      with open("token.json", "w") as token:
        token.write(self.creds.to_json())

  def load(self,email_list,subject,message_body,notes_doc):
    self.emailList = email_list
    self.notePath = notes_doc
    self.subject = subject
    self.messageBody = message_body

  def run(self):
    self.gmail_send_message(self.emailList,self.subject,self.messageBody,self.notePath)

  def gmail_send_message(self,to,sub="meeting notes",mes="The meeting notes are attached",attachment=None):
    """Create and send an email message
    Print the returned message id
    Returns: Message object, including message id

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    try:
      service = build("gmail", "v1", credentials=self.creds)
      message = EmailMessage()

      #Set the message
      message.set_content(mes)

      if attachment:
        with open(attachment,'rb') as fileToAttach:
          file_data = fileToAttach.read()
          file_name = os.path.basename(attachment)
          message.add_attachment(file_data,maintype='application',subtype='octet-stream',filename=file_name)

      # If `to` is a list of email addresses, join them with commas
      if isinstance(to, list):
        to = ', '.join(to)  # Join email addresses with a comma

      message["To"] = to
      message["From"] = "noreply@doesntmatter.com"
      #Set the Subject
      message["Subject"] = sub

      # encoded message
      encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

      create_message = {"raw": encoded_message}
      # pylint: disable=E1101
      send_message = (
          service.users()
          .messages()
          .send(userId="me", body=create_message)
          .execute()
      )
      print(f'Message Id: {send_message["id"]}')
    except HttpError as error:
      print(f"An error occurred with sending the message")
      send_message = None
    return send_message 


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

