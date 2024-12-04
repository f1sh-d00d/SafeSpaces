# Project: Audio/Video Transcription and Email Summary System

This project consists of two Python programs that process audio and video files, transcribe them, generate summaries, and allow users to send the results via email. The system uses machine learning models, such as Whisper for transcription and Ollama for summarization, as well as the Gmail API for email sending.

### Table of Contents
1. [App.py - Streamlit Web Interface](#App.py---streamlit-web-interface)
2. [AppModels.py - Command-Line Tool](#AppModels.py---command-line-tool)
3. [Prerequisites](#prerequisites)
4. [Usage](#usage)
5. [License](#license)

---

## App.py - Streamlit Web Interface

This program provides a web interface for users to upload audio/video files, transcribe them, generate summaries, and send the transcriptions as emails.

### Features:
- **Upload Audio/Video**: Users can upload audio or video files in `.mp4`, `.mov`, `.mp3`, `.wav` formats.
- **Transcription**: The app transcribes audio to text using the Whisper model.
- **Summarization**: After transcription, the app generates a summary of the text using the Ollama model.
- **Email Handling**: Users can add email addresses to a recipient list, and the summary can be emailed to those recipients.
- **User Interface**: Built using Streamlit with custom styling and easy-to-use navigation.

### Key Libraries:
- `streamlit`: For building the web interface.
- `pydub`, `librosa`, `moviepy`: For audio extraction and processing.
- `whisper`: For audio transcription.
- `Ollama`: For summarization.
- `google-auth`, `googleapiclient`: For Gmail API integration.

---

## AppModels.py - Command-Line Tool

### Overview

This system provides functionality for:
1. **Audio Extraction**: Extracts audio from video files.
2. **Transcription**: Transcribes the extracted audio to text using the Whisper model.
3. **Summarization**: Summarizes the transcribed text using the Ollama model.
4. **Emailing**: Sends the summary via email using the Gmail API.

The system is modular, with each step (audio extraction, transcription, summarization, email) encapsulated in separate classes, following the **BaseModel** pattern.

---

### Classes and Functionality

#### BaseModel

The `BaseModel` class serves as a generic base class for all models in this system. It defines two methods:
- `load()`: A placeholder for loading necessary data or files.
- `run()`: A placeholder for running the model's process.

#### AudioExtractModel

The `AudioExtractModel` class is responsible for extracting audio from video files. It takes a video file path, extracts the audio, converts it to mono, and returns the audio path.
- `load(video_path)`: Loads the video file for processing.
- `run()`: Extracts audio from the video, saves it to a file, and converts it to mono.

#### TranscriptModel

The `TranscriptModel` class transcribes the extracted audio into text using the Whisper model.
- `load(audio_path)`: Loads the audio file to be transcribed.
- `run()`: Transcribes the audio and returns the transcribed text.

#### SummaryModel

The `SummaryModel` class takes the transcribed text and generates a summary using the Ollama model. The summarized text is saved in a file.
- `load(transcript_text)`: Loads the transcribed text to be summarized.
- `run()`: Summarizes the transcript and saves the summary to a text file.

#### EmailModel

The `EmailModel` class is responsible for sending the summarized meeting notes via email using the Gmail API. It requires OAuth2 credentials for Gmail authentication.
- `load(email_list, subject, message_body, notes_doc)`: Loads email recipient list, subject, message body, and notes document.
- `run()`: Sends an email with the meeting notes as an attachment.
- `gmail_send_message()`: Creates and sends the email message.

---

## Prerequisites

STEP 1: install all dependencies needed in the requirements.txt file
using the following command: 

You can install them using `pip`:
```bash
pip install -r requirements.txt
```

STEP 2: After installing all the packages from requirements.txt, 
install "ffmpeg" based on your operating system as listed below:

- on Ubuntu or Debian
```bash
sudo apt update && sudo apt install ffmpeg
```

- on Arch Linux
```bash
sudo pacman -S ffmpeg
```

- on MacOS using Homebrew (https://brew.sh/)
```bash
brew install ffmpeg
```

- on Windows using Chocolatey (https://chocolatey.org/)
```bash
choco install ffmpeg
```

- on Windows using Scoop (https://scoop.sh/)
```bash
scoop install ffmpeg
```

STEP 3: Add a file named `credentials.json`, containing the connection information for a google cloud project that allows for the sending of an email via a connected account. A tutorial for how to set up said project can be found at https://developers.google.com/gmail/postmaster/quickstart/python

An example of what the inside of the file should look like is:
```json
{"installed":{"client_id":"xxxxxxxxx-xxxxxxxxxxxxx.apps.googleusercontent.com","project_id":"xxxxxxxxx","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"xxxxxxx-xxxxxxxxxxxxxxxxx","redirect_uris":["http://localhost"]}}
```

---

## Usage

To get started with the program, follow these steps:

1. **Navigate to the project directory**:
   Open your terminal or command prompt and navigate to the folder containing the project files.

2. **Run the program**:
   Execute the following command to start the app.

```bash
streamlit run app.py
```

   This will launch the program and automatically open a new tab in your default web browser, displaying the user interface.

3. **Upload a file**:
   From the UI, select the file you want to upload. The program will automatically begin the transcription and summarization process.

4. **View the results**:
   Once the transcription and summarization are complete, the summarized text will be displayed on the screen.

5. **Download or email the results**:
   - **Download the transcription**: You can download the summarized text as a `.txt` file by clicking the download button.
   - **Send as email**: If you'd like to send the summary via email, enter the recipient's email address into the provided field. After entering an email address, click the "Add" button to add more recipients if needed.

6. **Sending the email**:
   After all desired email addresses have been added, click the "Send" button to send the email with the summarized text attached.

   > **Note**: If this is your first time running the app, you'll be prompted to sign in to your Gmail account. The Gmail account you sign in with will be used as the sender's email.
