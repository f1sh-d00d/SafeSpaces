from vosk import Model, KaldiRecognizer
import moviepy.editor as mp
import speech_recognition as sr
import librosa
import torch
import soundfile as sf
import sys
import wave
import json

class Model:
    def load(self):
        pass

    def run(self):
        pass

class AudioExtractModel(Model):
    def __init__(self):
        self.audio_path = "meeting_audio.wav"
        self.viedo_path = None

    def load(self, video_path):
        '''sets model's video'''
        self.video_path = video_path

    def run(self):
        '''returns path to audio extracted from video'''
        video = mp.VideoFileClip(self.video_path)              #extract audio
        video.audio.write_audiofile(self.audio_path)        #write extracted audio to file found at path

        #get sample rate
        with wave.open(self.audio_path, "rb") as fin:
            sample_rate = fin.getframerate()
            print(f"Sample Rate: {sample_rate}")

        return self.audio_path                              #return path


class TranscriptModel(Model):
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def load(self, audio_path):
        self.audio_file = audio_path

    def run(self):
        with sr.AudioFile(self.audio_file) as fin:
            duration = fin.DURATION  # Total duration of audio in seconds
            chunk_size = 30  # Set chunk size to 30 seconds (or adjust as needed)
            text = ""

            for start in range(0, int(duration), chunk_size):
                fin = sr.AudioFile(self.audio_file)
                with fin as audio_file:
                    # Move to the starting position of the chunk
                    fin.seek(start * fin.SAMPLERATE)
                    # Read the next chunk of audio
                    data = self.recognizer.record(audio_file, duration=chunk_size)

                    # Try to recognize the audio chunk
                    try:
                        text += self.recognizer.recognize_google(data) + " "
                    except sr.UnknownValueError:
                        text += "[Unrecognized audio] "
                    except sr.RequestError:
                        text += "[Service error] "

        # Write the full transcription to a file
        with open("MeetingText.txt", "w") as fout:
            fout.write(f"Meeting Transcript:\n{text}")


def main():
    file_name = sys.argv[1]
    audio_model = AudioExtractModel()
    audio_model.load(file_name)
    audio_path = audio_model.run()

    #transcriber = TranscriptModel()
    #transcriber.load(audio_path)
    #transcriber.run()



if __name__ == "__main__":
    main()

