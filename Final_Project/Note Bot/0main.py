import moviepy.editor as mp
import speech_recognition as sr
import librosa
import torch
import soundfile as sf
import sys

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
        return self.audio_path                              #return path


class TranscriptModel(Model):
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def load(self, audio_path):
        self.audio_file = audio_path

    def run(self):
        with sr.AudioFile(self.audio_file) as fin:
            data = self.recognizer.record(fin)

        text = self.recognizer.recognize_google(data)

        with open ("MeetingText.txt", "w") as fout:
            fout.write(f"Meeting Transcript:\n{text}")



def main():
    file_name = sys.argv[1]
    audio_model = AudioExtractModel()
    audio_model.load(file_name)
    audio_path = audio_model.run()

    transcriber = TranscriptModel()
    transcriber.load(audio_path)
    transcriber.run()



if __name__ == "__main__":
    main()

