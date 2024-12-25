
# [{'word': 'Kind', 'type': 'noun', 'article': 'das', 'plural_form': 'Kinder', 'definitions_and_examples': [{'definition': 'junger Mensch im Alter von 0 bis etwa 12 Jahren', 'examples': 'Die Kinder spielen im Hof.'}]}, 
#  {'word': 'Kind', 'type': 'noun', 'article': 'das', 'plural_form': 'Kinder', 'definitions_and_examples': [{'definition': 'noch nicht geborener Mensch', 'examples': 'Sie erwartet / bekommt ein Kind.'}]}, 
#  {'word': 'Kind', 'type': 'noun', 'article': 'das', 'plural_form': 'Kinder', 'definitions_and_examples': [{'definition': 'Tochter oder Sohn als unmittelbarer Nachkomme', 'examples': 'Ich bin selbst ein adoptiertes / uneheliches Kind.'}]}]

def generate_card(entry, deck_name):
    word = entry["word"]
    word_with_article = entry["article"] + " " + entry["word"]

    definition = entry["definition_and_example"]["definition"]
    # there might not be an example
    example = entry["definition_and_example"].get("example", "")

    
    return {
        "deckName": deck_name,
        "modelName": "Basic",
        "fields": {
            "Front": f"Example: {example_with_highlight}",
            "Back": f"Definition: {definition}",
        },
        "tags": ["language", language],
        "options": {
            "allowDuplicate": False,
        },
    }
# def generate_card(entry, deck_name):
#     """
#     Converts a parsed word entry into an Anki card dictionary.
#     """
#     word = entry["word"]
#     definition = entry["definition"]
#     example = entry["example"]

#     # Highlight the word in the example sentence
#     example_with_highlight = example.replace(word, f"<span class='highlight'>{word}</span>")

#     return {
#         "deckName": deck_name,
#         "modelName": "Basic",
#         "fields": {
#             "Front": f"Example: {example_with_highlight}",
#             "Back": f"Definition: {definition}",
#         },
#         "tags": ["language", language],
#         "options": {
#             "allowDuplicate": False,
#         },
#     }
