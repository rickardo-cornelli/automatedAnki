
from word_processor import get_base_word_in_sentence

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

def generate_card(entry, deck_name, language):
    word = entry["word"]
    

    definition = entry["definition_and_example"]["definition"]
    # there might not be an example
    example = entry["definition_and_example"].get("example", "")

    example_with_word_highlighted = highlight_word_in_example(word, example, language)

    word = highlight_word(word)
    if entry["type"] == "noun":
        word = highlight_word(entry["article"]) + " " + word

    
    return {
        "deckName": deck_name,
        "modelName": "Basic",
        "fields": {
            "Front": f"{example_with_word_highlighted}",
            "Back": f"{word} = {definition}",
        },
        "tags": ["language", language],
        "options": {
            "allowDuplicate": False,
        },
    }
