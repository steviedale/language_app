from google.cloud import texttospeech
import pandas as pd
import os
import time
# for guid generation
import uuid


DATA_DIR = 'data'

SAVE_DIR = 'data/audio'
DF_PATH = 'data/dataframe.csv'

VOICES = {
    'it': {
        'male': 'it-IT-Wavenet-D',
        'female': 'it-IT-Wavenet-C',
    },
    'en': {
        'male': 'en-US-Wavenet-D',
        'female': 'en-US-Wavenet-C',
    },
}

class TextToSpeech:

    def __init__(self):

        if not os.path.exists(SAVE_DIR):
            os.makedirs(SAVE_DIR)

        if not os.path.exists(DF_PATH):
            self.df = pd.DataFrame(columns=[
                'text_hash', 'text', 'audio_file', 'synthesis_time', 
                'voice_name', 'speaking_rate', 'pitch'
            ])
        else:
            self.df = pd.read_csv(DF_PATH)

        self.client = texttospeech.TextToSpeechClient()
        self.voice = texttospeech.VoiceSelectionParams(language_code="it-IT")
        self.audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
    
    # destructor
    def __del__(self):
        self.save()

    def synthesize(self, text, speaking_rate=0.75, voice_name="it-IT-Wavenet-D", pitch=0):
        self.voice.name = voice_name
        self.audio_config.speaking_rate = speaking_rate
        self.audio_config.pitch = pitch
        synthesis_input = texttospeech.SynthesisInput(text=text)

        # hash text
        guid = uuid.uuid5(uuid.NAMESPACE_DNS, str(hash(f"{text}{voice_name}{speaking_rate:.2f}{pitch}")))

        audio_file = f'{SAVE_DIR}/{guid}.mp3'

        # check if text already exists
        if self.df[(self.df['text'] == text) & (self.df['speaking_rate'] == speaking_rate)].shape[0] > 0:
            s_df = self.df[self.df['text'] == text]
            assert(s_df.shape[0] == 1)
            row = s_df.iloc[0]
            assert(row['guid'] == guid)
            assert(row['audio_file'] == audio_file)

        else:
            print("synthesizing...")
            # Synthesize speech
            t0 = time.perf_counter()
            response = self.client.synthesize_speech(
                input=synthesis_input, voice=self.voice, audio_config=self.audio_config)
            t1 = time.perf_counter()
            synthesis_time = t1 - t0

            # save audio
            with open(audio_file, "wb") as out:
                out.write(response.audio_content) 

            # store in dataframe
            self.df.loc[self.df.shape[0]] = [guid, text, audio_file, synthesis_time, voice_name, speaking_rate, pitch]
            row = self.df.iloc[-1]

        return dict(row)

    def save(self):
        self.df.to_csv(DF_PATH, index=False)
        print(f"Dataframe saved to {DF_PATH}")


if __name__ == '__main__':
    tts = TextToSpeech()

    phrase = 'vorrei un tavolo per due vicino alla finestra'
    ret = tts.synthesize(phrase, speaking_rate=0.7)

    print(ret)