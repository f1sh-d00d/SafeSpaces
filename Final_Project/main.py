from vosk import Model, KaldiRecognizer
import moviepy.editor as mp
import speech_recognition as sr
import librosa
import torch
import soundfile as sf
import sys
import wave
import json

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

    def load(self, audio_path):
        self.audio_path = audio_path

    def run(self):
        model = Model(self.model_path)                      #initialize Vosk model
        fin = wave.open(self.audio_path, "rb")
        rate = fin.getframerate()
        print(f"Sample Rate: {rate}")

        recognizer = KaldiRecognizer(model, rate)           #create audio recognizer from model, with file's sample rate

        print("Starting Transcription...")
        with open("MeetingText.txt", "w") as fout:
            while True:
                data = fin.readframes(2000)                     #listen to audio in chuncks to get full audio
                if len(data) == 0:
                    break                                       #exit loop if there is no more audio
                if recognizer.AcceptWaveform(data):
                    result = recognizer.Result()
                    text = json.loads(result)["text"]
                    fout.write(f"{text}\n")
            
#FIXME - add summary model class using llama 

def main():
    file_name = sys.argv[1]
    audio_model = AudioExtractModel()
    audio_model.load(file_name)
    audio_path = audio_model.run()

    transcriber = TranscriptModel()
    transcriber.load(audio_path)
    transcriber.run()

# Added: function to process video from UI
def process_video(video_path):
    """
    A function to process the video and return the transcription text for integration with UI.
    """
    audio_model = AudioExtractModel()
    audio_model.load(video_path)
    audio_path = audio_model.run()

    transcriber = TranscriptModel()
    transcriber.load(audio_path)
    transcriber.run()

    with open("MeetingText.txt", "r") as file:  # Open the transcription file
        return file.read()  # Return the transcription text

if __name__ == "__main__":
    main()