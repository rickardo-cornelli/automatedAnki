from src.word_processor import get_base_word_in_sentence
from src.media_fetchers.image_fetcher import get_image
from src.media_fetchers.audio_fetcher import fetch_audio

def highlight_word(word):
    return f"<span style='color: lightgreen;'>{word}</span>"

def highlight_word_in_example(word, example_sentence, language):

    if (not example_sentence):
        highlighted_word = highlight_word(word)
        return highlighted_word
    
    else:
        word_to_highlight_in_sentence = get_base_word_in_sentence(example_sentence, word, language)
    
        highlighted_example = example_sentence.replace(
            word_to_highlight_in_sentence, highlight_word(word_to_highlight_in_sentence)
        )
    return highlighted_example


def generate_card(entry, deck_name, language, include_image=True, include_audio = True):
    word = entry["word"]
    

    definition = entry["definition_and_example"]["definition"]
    # there might not be an example
    example = entry["definition_and_example"].get("example", "")

    example_with_word_highlighted = highlight_word_in_example(word, example, language)
    
    audio_data = {}
    image_data = {}
    if (include_audio):
        audio_data = fetch_audio(word, language)
    
    if (include_image):
        image_data = get_image(word,language)
    word = highlight_word(word)
    if (entry["type"] == "noun"):
        word = highlight_word(entry["article"]) + " " + word

    anki_card =  {
    
        "deckName": deck_name,
        "modelName": "Basic",
        "fields": {
            "Front": f"{example_with_word_highlighted}",
            "Back": f"{word} = {definition}"
        },
        "tags": ["language", language],
        "options": {
            "allowDuplicate": False,
        },
    }

    if (include_audio and audio_data):
        anki_card["fields"]["Back"] += f"<br>[sound:{audio_data['filename']}]"
    if(include_image and image_data):
        anki_card["fields"]["Back"] += f'<br><img src="{image_data["filename"]}">'
    return anki_card, audio_data, image_data

