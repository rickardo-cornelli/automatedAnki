from word_processor import get_base_word_in_sentence
from gtts import gTTS
import base64
import requests
import os


AUDIO_DIR = "audio"


if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

def highlight_word(word):
    return f"<span style='color: lightgreen;'>{word}</span>"

# fix: for the example "the kinder spielen im hof", i get : "Example: Die Kind spielen im Hof."
def highlight_word_in_example(word, example_sentence, language):

    if(not example_sentence):
        highlighted_word = highlight_word(word)
        return highlighted_word
    
    else:
        word_to_highlight_in_sentence = get_base_word_in_sentence(example_sentence, word, language)
    
        highlighted_example = example_sentence.replace(
            word_to_highlight_in_sentence, highlight_word(word_to_highlight_in_sentence)
        )
    return highlighted_example

def audio_file_exists(word):
    file_path = f"audio/{word}.mp3"
    return os.path.exists(file_path)

def get_audio(word, language="en"):

    file_path = f"audio/{word}.mp3"

    if not audio_file_exists(word):
        tts = gTTS(text=word, lang=language)
        tts.save(file_path)
    
    return {"filename": f"{word}.mp3", "filepath": file_path}


def generate_card(entry, deck_name, language, include_audio = True):
    word = entry["word"]
    

    definition = entry["definition_and_example"]["definition"]
    # there might not be an example
    example = entry["definition_and_example"].get("example", "")

    example_with_word_highlighted = highlight_word_in_example(word, example, language)
    
    audio_data = {}
    # Generate base64-encoded audio data
    if include_audio:
        audio_data = get_audio(word, language)
    

    word = highlight_word(word)
    if entry["type"] == "noun":
        word = highlight_word(entry["article"]) + " " + word

    anki_card =  {
    
        "deckName": deck_name,
        "modelName": "Basic",
        "fields": {
            "Front": f"{example_with_word_highlighted}",
            "Back": f"{word} = {definition}" + (f"<br>[sound:{audio_data['filename']}]" if include_audio else ""),
        },
        "tags": ["language", language],
        "options": {
            "allowDuplicate": False,
        },
       
    }
    return anki_card, audio_data

