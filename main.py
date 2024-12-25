from word_processor import get_definition, get_base_word_in_sentence
from card_generator import generate_card
from anki_sender import add_card, add_cards_in_batch

print(get_base_word_in_sentence("les femmes", "femme", "fr"))

""" for entry in entries:
    generate_card(entry, "test") """


language = "fr"
entries = get_definition("femme", language)
cards = [generate_card(entry, "test", language) for entry in entries]

add_cards_in_batch(cards)
