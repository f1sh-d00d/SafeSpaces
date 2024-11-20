# Importing libraries  
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

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly","https://www.googleapis.com/auth/gmail.send","https://mail.google.com/","https://www.googleapis.com/auth/gmail.modify","https://www.googleapis.com/auth/gmail.compose"]


class BaseModel:
  '''Generic Model Class'''
  def load(self):
    pass

  def run(self):
    pass
    
class EmailModel(BaseModel):
  def __init__(self):
    self.emailList = None
    self.notePath = None
    self.creds = None
    self.subject = None
    self.messageBody = None

    if os.path.exists("token.json"):
      self.creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not self.creds or not self.creds.valid:
      if self.creds and self.creds.expired and self.creds.refresh_token:
        flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
        )
        self.creds = flow.run_local_server(port=0)
      else:
        flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
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