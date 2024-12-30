from src.word_processor import get_definition
from src.card_generator import generate_card
from src.anki_sender import add_card, add_cards_in_batch, store_media_file


language = "fr"
include_audio = True
include_image = True

entries = get_definition("lion", language)

card, audio_data, image_data = generate_card(entries[0],"test",language, include_image, include_audio)

if audio_data:
    store_media_file(audio_data["filename"], audio_data["filepath"])
if image_data:
    store_media_file(image_data["filename"], image_data["filepath"])
add_card(card)
