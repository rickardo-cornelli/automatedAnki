from word_processor import get_definition, get_base_word_in_sentence
from card_generator import generate_card
from anki_sender import add_card, add_cards_in_batch, store_audio_file


language = "fr"
include_audio = True
entries = get_definition("femme", language)
card, audio_data = generate_card(entries[0],"test",language, include_audio)

if audio_data:
    store_audio_file(audio_data["filename"], audio_data["filepath"])
    
add_card(card)
