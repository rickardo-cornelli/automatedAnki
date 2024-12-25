from word_processor import get_definition, find_base_word_in_sentence
from card_generator import generate_card
entries = [{'word': 'Kind', 'type': 'noun', 'article': 'das', 'plural_form': 'Kinder', 'definition_and_example': {'definition': 'junger Mensch im Alter von 0 bis etwa 12 Jahren', 'example': 'Die Kinder spielen im Hof.'}}, {'word': 'Kind', 'type': 'noun', 'article': 'das', 'plural_form': 'Kinder', 'definition_and_example': {'definition': 'noch nicht geborener Mensch', 'example': 'Sie erwartet / bekommt ein Kind.'}}, {'word': 'Kind', 'type': 'noun', 'article': 'das', 'plural_form': 'Kinder', 'definition_and_example': {'definition': 'Tochter oder Sohn als unmittelbarer Nachkomme', 'example': 'Ich bin selbst ein adoptiertes / uneheliches Kind.'}}]

""" for entry in entries:
    generate_card(entry, "test") """

base_word = "boire"

examples = [

    "il buvait un café",
    "je bois un truc",
    "vous buvez quoi?",
    "il a beaucoup bu"
]

""" for ex in examples:
    print(find_base_word_in_sentence(ex, base_word, "fr")) """