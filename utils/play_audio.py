from pygame import mixer
import time


def play_audio(file_path):
    mixer.init()
    mixer.music.load(file_path)
    mixer.music.play()
    # wait for music to finish playing
    while mixer.music.get_busy():
        time.sleep(0.1)


if __name__ == '__main__':
    file_path = '/Users/stevie/repos/language_app/data/audio/65ab337b-94fb-53b2-8309-597130861e84.mp3'
    play_audio(file_path)