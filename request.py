import json
import sys
import os
import requests
import spacy
from dotenv import load_dotenv

# Preload supported spaCy models
SPACY_MODELS = {
    "de": spacy.load("de_core_news_sm"),  # German
    "sv": spacy.load('sv_core_news_sm'),
    "fr": spacy.load('fr_core_news_sm')
}
# the articles in the languages currently supported
LANGUAGE_ARTICLES = {
    "de": {"feminine": "die", "masculine": "der", "neuter": "das"},
    "fr": {"feminine": "la", "masculine": "le"},
    "es": {"feminine": "la", "masculine": "el"},
}
LANGUAGE_REFLEXIVE_PRONOUN = {
    "de": {"1st":"mich", "2nd":"dich", "3rd":"sich"},
    "fr": {"1st": "me", "2nd": "te", "3rd":"se"}
}

LANGUAGE_CONJUGATION_HELP_VERB = {
    "de" : {"Perfekt mit sein": "ist", "Perfekt mit haben": "habe"}
}

AUTHORIZATION_ERROR = "Authorization Error"
UNKNOWN_ERROR = "Unknown Error"
INVALID_RESPONSE = "Invalid Response"
VALID_RESPONSE = "Valid Response"
TIMEOUT = "Timeout"
REQUEST_EXCEPTION = "Request Exception"

def isNoun(headword):
    return headword["pos"] == "noun"

def isVerb(headword):
    return headword["pos"] == "verb"

def get_article(gender, language):
    articles = LANGUAGE_ARTICLES.get(language, {})
    return articles.get(gender, "unknown gender") if articles else "Language currently not supported"

def get_reflexive_article(person, language):
    articles = LANGUAGE_REFLEXIVE_PRONOUN.get(language, {})
    return articles.get(person, "unknown article") if articles else "Languages currently not supported"

def get_help_verb(language, conjugates_with):
    help_verbs = LANGUAGE_CONJUGATION_HELP_VERB.get(language, {})
    return help_verbs.get(conjugates_with, "unknown help verb") if help_verbs else "Languages currently not supported"

def get_plural_form(inflections):
    plural_form = ""
    for inflection in inflections:
        if(inflection["number"] == "plural"):
            plural_form = inflection["text"]
    return plural_form

def parse_noun_data(headword, language):
    word = headword["text"]
    gender = headword.get("gender", "unknown")
    article = get_article(gender, language)
    inflections = headword.get("inflections", {})

    plural_form = get_plural_form(inflections) if inflections else ""

    noun_data = {"word": word, "article": article, "plural_form":plural_form}
    
    return noun_data

def get_verb_conjugation(headword, sense, language):
    """
    Gets the verb conjugations of a verb
    valency indicates whether it conjugates with have or be in French, Spanish, and German
    Valency and the help verb can be found in either headword or in sense
    """
    word = headword["text"]
    # sleichen reflexive -> sich sleichen valen
    valency = headword.get("valency") or sense.get("valency")
    word = get_reflexive_article("3rd", language) + word if valency == "reflexive" else word
    # 
    conjugates_with = headword.get("range_of_application") or sense.get("range_of_application")
    help_verb = get_help_verb(language, conjugates_with)
    
    return {}
def get_definition_and_example(sense):
    definitions_and_examples = []
    definition = sense.get('definition')
    examples = sense.get('examples', [])

    definitions_and_examples.append({
        'definition': definition,
        'examples': examples[0]["text"] if examples else ""
    })

    return definitions_and_examples

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
        print(response_results)
        results = response_results if (isinstance(response_results, list)) else [response_results]
        
        for result in results:
            word_entry = {}
            headwords = result["headword"] if isinstance(result["headword"], list) else [result["headword"]]
            for sense in result["senses"]:
                if(isNoun(headwords[0])):
                    word_entry = parse_noun_data(headwords[0], language)
                if(isVerb(headwords[0])):
                    word_entry = get_verb_conjugation(headwords[0], sense, language)

                word_entry["definitions_and_examples"] = get_definition_and_example(sense)
                entries.append(word_entry)
    print(entries)

def get_base_word(word, language):
    # Check if spaCy model for the language is loaded
    if language in SPACY_MODELS:
        nlp = SPACY_MODELS[language]
        doc = nlp(word)
        for token in doc:
            return token.lemma_
    else:
        return f"spaCy model not available for language '{language}'"

# Test words in multiple languages
get_definition("schleichen", "de")
