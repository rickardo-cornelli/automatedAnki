from gtts import gTTS
import os


AUDIO_DIR = "media/audio"

if (not os.path.exists(AUDIO_DIR)):
    os.makedirs(AUDIO_DIR)


def audio_file_exists(file_path):
    return os.path.exists(file_path)

def fetch_audio(word, language="en"):

    file_path = os.path.join(AUDIO_DIR, f"{word.replace(' ', '_')}.jpg")

    if not audio_file_exists(word):
        tts = gTTS(text=word, lang=language)
        tts.save(file_path)
    
    return {"filename": f"{word}.mp3", "filepath": file_path}