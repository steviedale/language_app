from google.cloud import texttospeech
import pandas as pd
import os
import time
# for guid generation
import uuid
import numpy as np
import hashlib


DATA_DIR = 'data'

SAVE_DIR = 'data/audio'
DF_PATH = 'data/dataframe.csv'

VOICES = {
    'italian': {
        'male': 'it-IT-Wavenet-D',
        'female': 'it-IT-Wavenet-C',
    },
    'english': {
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
                'hash', 'text', 'audio_file', 'synthesis_time', 
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

    def synthesize(self, text, speaking_rate=0.75, voice_name="it-IT-Wavenet-D", pitch=0, verbose=False):
        self.voice.name = voice_name
        self.audio_config.speaking_rate = speaking_rate
        self.audio_config.pitch = pitch

        # hash text
        param_str = f"{text}{voice_name}{speaking_rate:.2f}{pitch:.2f}"
        hash_object = hashlib.sha256(param_str.encode('utf-8'))
        hash_key = hash_object.hexdigest()

        audio_file = f'{SAVE_DIR}/{hash_key}.mp3'

        # check if text already exists
        match_df = self.df[self.df['hash'] == hash_key]
        if len(match_df) > 0:
            if verbose:
                print("found in dataframe")
            match_df = self.df[self.df['hash'] == hash_key]
            row = match_df.iloc[0]
            assert(len(match_df) == 1)
            assert(row['text'] == text)
            assert(row['speaking_rate'] == speaking_rate)
            assert(row['pitch'] == pitch)
            assert(row['voice_name'] == voice_name)
            assert(row['hash'] == hash_key)
            assert(row['audio_file'] == audio_file)

        else:
            if verbose:
                print("synthesizing...")
            # Synthesize speech
            t0 = time.perf_counter()
            synthesis_input = texttospeech.SynthesisInput(text=text)
            response = self.client.synthesize_speech(
                input=synthesis_input, voice=self.voice, audio_config=self.audio_config)
            t1 = time.perf_counter()
            synthesis_time = t1 - t0

            # save audio
            with open(audio_file, "wb") as out:
                out.write(response.audio_content) 

            # store in dataframe
            self.df.loc[self.df.shape[0]] = [
                hash_key, text, audio_file, synthesis_time, voice_name, speaking_rate, pitch
            ]
            row = self.df.iloc[-1]
        data = dict(row)
        # convert np.float to float
        # convert np.int to int
        for k, v in data.items():
            if type(v) is np.float64 or type(v) is np.float32 or type(v) is np.float16:
                data[k] = float(v)
            if type(v) is np.int64 or type(v) is np.int32 or type(v) is np.int16:
                data[k] = int(v)
        return data

    def save(self):
        self.df.to_csv(DF_PATH, index=False)
        print(f"Dataframe saved to {DF_PATH}")


if __name__ == '__main__':
    tts = TextToSpeech()

    # phrase = 'vorrei un tavolo per due vicino alla finestra'
    phrase = 'this is a test script that should hopefully take a few seconds to finish. Which will give me enought time to debug.'
    ret = tts.synthesize(phrase, speaking_rate=1.0, voice_name='en-US-Wavenet-D', pitch=0.0, verbose=True)

    print(ret)