import moviepy.editor as mp
import librosa
import soundfile as sf
import sys
import os

class BaseModel:
    '''Generic Model Class'''
    def load(self):
        pass

    def run(self):
        pass

class AudioExtractModel(BaseModel):
    def __init__(self):
        self.audio_path = "meeting_audio.wav"  # Valid file name
        self.video_path = None

    def load(self, video_path):
        '''sets model's video'''
        self.video_path = video_path

    def run(self):
        '''returns path to audio extracted from video'''
        # Extract audio from video
        video = mp.VideoFileClip(self.video_path)
        video.audio.write_audiofile(self.audio_path)

        # Convert to mono audio and save
        audio, sr = librosa.load(self.audio_path, mono=True, sr=None)
        sf.write(self.audio_path, audio, sr)
        print("Current working directory:", os.getcwd())

        return self.audio_path  # Return the path of the saved audio

def main():
    # file_name = sys.argv[1]
    file_name = "meeting1.mp4"
    audio_model = AudioExtractModel()
    audio_model.load(file_name)
    audio_path = audio_model.run()

if __name__ == "__main__":
    main()
