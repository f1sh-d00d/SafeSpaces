# Project: Audio/Video Transcription and Email Summary System

This project consists of two Python programs that process audio and video files, transcribe them, generate summaries, and allow users to send the results via email. The system uses machine learning models, such as Whisper for transcription and Ollama for summarization, as well as the Gmail API for email sending.

### Table of Contents
1. [Program 1 - Streamlit Web Interface](#program-1---streamlit-web-interface)
2. [Program 2 - Command-Line Tool](#program-2---command-line-tool)
3. [Prerequisites](#prerequisites)
4. [Setup and Installation](#setup-and-installation)
5. [Usage](#usage)
6. [License](#license)

---

## Program 1 - Streamlit Web Interface

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

### File Descriptions:
1. **`program_1.py`**: Main Streamlit web app script.
2. **`AppModels.py`**: Contains model classes (`AudioExtractModel`, `TranscriptModel`, `SummaryModel`, `EmailModel`).

---

## Program 2 - Command-Line Tool

This program is a command-line tool that accepts a video/audio file as input, extracts the audio, transcribes it, summarizes it, and sends the summary as an email. It works through the terminal and requires arguments to be passed for file processing.

### Features:
- **Audio Extraction**: Extracts audio from video files using `moviepy.editor` and `librosa`.
- **Transcription**: Uses the Whisper model to transcribe the audio to text.
- **Summarization**: Summarizes the transcript using the Ollama model.
- **Email Handling**: Sends an email with the summarized transcript as an attachment via Gmail API.
- **Command-Line Interface**: The program accepts a file path argument and processes the file in the terminal.

### Key Libraries:
- `moviepy`, `librosa`, `whisper`: For audio extraction and transcription.
- `Ollama`: For generating summaries.
- `google-auth`, `google-apiclient`: For Gmail API integration.

### File Descriptions:
1. **`program_2.py`**: The main script that runs the process from the command line.
2. **Model Classes**: The models for audio extraction, transcription, summarization, and email handling are defined in the same file.

---

## Prerequisites

Before running both programs, ensure that the following dependencies are installed:

### Dependencies for Program 1:
- Streamlit
- `moviepy`
- `pydub`
- `librosa`
- `whisper`
- `Ollama`
- `google-auth`
- `google-auth-oauthlib`
- `google-auth-httplib2`
- `google-api-python-client`
- `soundfile`

You can install them using `pip`:
```bash
pip install -r requirements.txt