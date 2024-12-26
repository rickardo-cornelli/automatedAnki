import json
import sys
import os
import requests
import spacy
from dotenv import load_dotenv

# Constants and mapping
SPACY_MODELS = {
    "de": spacy.load("de_core_news_sm"),  # German
    "fr": spacy.load('fr_core_news_sm'),
}

LANGUAGE_ARTICLES = {
    "de": {"feminine": "die", "masculine": "der", "neuter": "das"},
    "fr": {"feminine": "la", "masculine": "le"},
    "es": {"feminine": "la", "masculine": "el"},
}
LANGUAGE_REFLEXIVE_PRONOUN = {
    "de": {"1st":"mich", "2nd":"dich", "3rd":"sich"},
    "fr": {"1st": "me", "2nd": "te", "3rd":"se"},
    "es": {"1st": "me", "2nd": "te", "3rd": "se"}
}

LANGUAGE_CONJUGATION_HELP_VERB = {
    "de" : {"Perfekt mit sein": "sein", "Perfekt mit haben": "haben"}
}

LANGUAGE_HELP_VERB_CONJUGATION = {
    "fr" : {"être": {"1st":"suis", "2nd":"es", "3rd": "est"}, "avoir": {"1st":"ai", "2nd": "as", "3rd":"a"}},
    "de" : {"sein": {"1st": "bin", "2nd": "bist", "3rd": "ist", "haben": {"1st":"habe", "2nd": "hast", "3rd": "ist"}}}
}

AUTHORIZATION_ERROR = "Authorization Error"
UNKNOWN_ERROR = "Unknown Error"
INVALID_RESPONSE = "Invalid Response"
VALID_RESPONSE = "Valid Response"
TIMEOUT = "Timeout"
REQUEST_EXCEPTION = "Request Exception"

# Helper functions
def is_noun(headword):
    return headword["pos"] == "noun"

def is_verb(headword):
    return headword["pos"] == "verb"

def is_adjective(headword):
    return headword["pos"] == "adjective"

def get_article(gender, language):
    articles = LANGUAGE_ARTICLES.get(language, {})
    return articles.get(gender, "unknown gender") if articles else "Language currently not supported"

def get_definition_and_example(sense):
    definition = sense.get('definition')
    examples = sense.get('examples', [])

    definition_and_example = {
        'definition': definition,
        'example': examples[0]["text"] if examples else ""
    }

    return definition_and_example

def get_reflexive_article(person, language):
    articles = LANGUAGE_REFLEXIVE_PRONOUN.get(language, {})
    return articles.get(person, "unknown article") if articles else "Languages currently not supported"

def get_help_verb(language, conjugates_with):
    help_verbs = LANGUAGE_CONJUGATION_HELP_VERB.get(language, {})
    return help_verbs.get(conjugates_with, "unknown help verb") if help_verbs else "Languages currently not supported"

def get_help_verb_conjugation(help_verb, language, person):
    help_verbs = LANGUAGE_CONJUGATION_HELP_VERB.get(language)
    
    if help_verbs is None:
        return "Language currently not supported"
    
    help_verb_conjugations = help_verbs.get(help_verb, {})
    return help_verb_conjugations.get(person, "unknown help verb")

def get_plural_form(inflections):
    plural_form = ""
    for inflection in inflections:
        if(inflection["number"] == "plural"):
            plural_form = inflection["text"]
    return plural_form

# Parsing different kinds of words (nouns, verbs, adjectives)

def parse_noun_properties(headword, language):
    word = headword["text"]
    gender = headword.get("gender", "unknown")
    article = get_article(gender, language)
    inflections = headword.get("inflections", {})

    plural_form = get_plural_form(inflections) if inflections else ""

    noun_data = {"word": word, "type":"noun", "article": article, "plural_form":plural_form}
    
    return noun_data

# TODO: fix conjugations parsed are {'preterit': 'schlich', 'pastParticiple': 'unknown help verb geschlichen'} 
# I think it is because I call the wrong dictionary in get help verb conjugation
def get_verb_conjugations(inflections, valency, help_verb):
    conjugations = {}
    for inflection in inflections:
        
        conjugated_verb = inflection["text"]

        person = inflection.get("person", "3rd")
        reflexive_article = get_reflexive_article(person, "de") 

        if(inflection["tense"] == 'preterit'):
            conjugations["preterit"] = conjugated_verb + " " + reflexive_article if valency == 'reflexive' else conjugated_verb
        if(inflection["tense"] == 'present'):
            conjugations["present"] = reflexive_article + " " + conjugated_verb if valency == 'reflexive' else conjugated_verb
        if(inflection["tense"] == 'pastParticiple'):
            conjugated_help_verb = get_help_verb_conjugation(help_verb, "de", "3rd")
            conjugations["pastParticiple"] = conjugated_help_verb + " " + reflexive_article + " " + conjugated_verb if valency == 'reflexive' else conjugated_help_verb + " " + conjugated_verb

    return conjugations

"""
    Verb conjugations are found in inflections, a key-value pair in headword
    valency indicates whether it conjugates with have or be in French, Spanish, and German
    Valency and the help verb can be found in either headword or in sense
"""
def parse_verb_properties(headword, sense, language):
   
    word = headword["text"]
    # sleichen reflexive -> sich sleichen valen
    valency = headword.get("valency") or sense.get("valency")
    word = get_reflexive_article("3rd", language) + word if valency == "reflexive" else word
    
    # only German verbs have verb conjugations included in the Lexicala API
    if language == 'de':
        conjugates_with = headword.get("range_of_application") or sense.get("range_of_application")
        help_verb = get_help_verb(language, conjugates_with)
        inflections = headword.get("inflections", [])
        verb_conjugations = get_verb_conjugations(inflections, valency, help_verb)
    else:
        help_verb = None
        verb_conjugations = {}
    return {"word": word, "type": "verb", "valency": valency, "help_verb": help_verb, "conjugations": verb_conjugations}
    

def parse_entry(headword, sense, language):
    word_entry = {}
    if (is_noun(headword)):
        word_entry = parse_noun_properties(headword, language)
    elif (is_verb(headword)):
        word_entry = parse_verb_properties(headword, sense, language)
    elif(is_adjective(headword)):
        print("havent fixed adjective support yet")
    else:
        print(f"unidentified PoS: {headword["pos"]}")
    word_entry["definition_and_example"] = get_definition_and_example(sense)
    return word_entry

# returns a token, and if succesful: also returns the response
def call_api(url, headers, querystring):
    try: 
        response = requests.get(url, headers=headers, params=querystring, timeout=10)
        if (response.status_code == 403):
            return AUTHORIZATION_ERROR
        
        if (response.status_code != 200):
            return UNKNOWN_ERROR
        
        response_data = response.json()

        if not response_data["results"]:
            return INVALID_RESPONSE
        
        return VALID_RESPONSE, response_data["results"]

    except requests.exceptions.Timeout:
        return TIMEOUT
    except requests.exceptions.RequestException:
        return REQUEST_EXCEPTION


def get_definition(word, language="de"):
  
    load_dotenv(dotenv_path='Anki.env')
    base_word = get_base_word(word,language)
    RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
    RAPIDAPI_HOST = os.getenv('RAPIDAPI_HOST')

    url = "https://lexicala1.p.rapidapi.com/search-entries"
    querystring = {"text": base_word, "language": language, "analyzed": "true"}
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }
    result = call_api(url, headers, querystring)

    entries = []
    if(isinstance(result, tuple)):
        
        response_results = result[1]
        results = response_results if (isinstance(response_results, list)) else [response_results]

        for result in results:
            word_entry = {}
            headwords = result["headword"] if isinstance(result["headword"], list) else [result["headword"]]
            for sense in result["senses"]:
                word_entry = parse_entry(headwords[0], sense, language)
                entries.append(word_entry)
    return entries

def get_base_word(word, language):
    if language in SPACY_MODELS:
        nlp = SPACY_MODELS[language]
        doc = nlp(word)
        for token in doc:
            return token.lemma_
    else:
        return f"spaCy model not available for language '{language}'"

def get_base_word_in_sentence(sentence, base_word, language):
    if language in SPACY_MODELS:
        nlp = SPACY_MODELS[language]
        doc = nlp(sentence)

        for token in doc:
            if token.lemma_ == base_word:
                return token.text
    
    return None