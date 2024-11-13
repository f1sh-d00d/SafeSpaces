import streamlit as st 
import whisper 
from tempfile import NamedTemporaryFile
from io import BytesIO
from pydub.utils import mediainfo


def speech_to_text(audio_file):
    model= whisper.load_model("base")

    input_audio= audio_file.read()

    with NamedTemporaryFile(suffix=".tmp", delete=False) as temp_file: 
        temp_file.write(input_audio)
        temp_file_path = temp_file.name #store file path 

    
    info= mediainfo(temp_file_path) #get the audio file format 

    audio_format = info["format_name"]

    if "mp3" in audio_format:
        suffix = ".mp3"
    elif "wav" in audio_format:
        suffix = ".wav"
    else: 
        raise ValueError(f"{audio_format} is an unsupported audio format")

    result= model.transcribe(temp_file_path, fp16=False)

    return result['text']

def forstreamlit():
    audio_file= st.file_uploader("Upload your audio file here: ", type=["mp3", "wav"])
    if audio_file is not None:
        st.write(f"Uploading your {audio_file.name}")
        transcription= speech_to_text(audio_file)
        st.write("Transcribed Text: ", transcription)

        with open(f"{audio_file.name}.txt", "w") as file:
            file.write(transcription)
        with open(f"{audio_file.name}.txt", "r") as file:
            transcribed_text= file.read()

        column_one, column_two= st.columns(2)
        with column_one: 
            st.download_button(
                label="Download Full Transcript",
                data=transcribed_text,
                file_name=f"{audio_file.name}.txt",
                mime="text/plain"
            )
        with column_two:
            st.button(
                label= "Email Full Transcript"
            )

forstreamlit()
