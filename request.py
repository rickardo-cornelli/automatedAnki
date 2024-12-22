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

AUTHORIZATION_ERROR = "Authorization Error"
UNKNOWN_ERROR = "Unknown Error"
INVALID_RESPONSE = "Invalid Response"
VALID_RESPONSE = "Valid Response"
NOUN = "Noun"
NOT_NOUN = "Not Noun"
TIMEOUT = "Timeout"
REQUEST_EXCEPTION = "Request Exception"

def isNoun(headword):
    return headword["pos"] == "noun"

def get_article(gender, language):
    articles = LANGUAGE_ARTICLES.get(language, {})
    return articles.get(gender, "unknown gender") if articles else "Language currently not supported"

def parse_noun_data(headword, language):
    
    gender = headword.get("gender", "unknown")
    article = get_article(gender, language)
    inflections = headword.get("inflections", {})
    print(f"headword is {headword}")

    print(f"inflections is {inflections}")

    plural_form = inflections[1].get("text") if inflections and len(inflections) > 1 else ""

    noun_data = {"article": article, "plural_form":plural_form, "definitions": []}
    
    defs = []
    for sense in response_data[0].get("senses", {}):
        meaning = {}
        examples = sense.get("examples", [])
        if examples:
            meaning["example"] = sense["examples"][0].get("text", "")
            meaning["definition"] = sense.get("definition", "")
        defs.append(meaning)

    noun_data["definitions"] = defs
    print(noun_data)
    return noun_data



def call_api(url, headers, querystring, language):
    try: 
        response = requests.get(url, headers=headers, params=querystring, timeout=10)
        #print(response)
        if (response.status_code == 403):
            return AUTHORIZATION_ERROR
        
        if (response.status_code != 200):
            #print(f"Request failed with status code {response.status_code}")
            return UNKNOWN_ERROR
        
        response_data = response.json()
        #print(response_data)
        if not response_data["results"]:
            #print(f"No valid response for {base_word} in {language}, verify the spelling of both")
            return INVALID_RESPONSE
        else:
            return VALID_RESPONSE, response_data["results"]

    except requests.exceptions.Timeout:
        return TIMEOUT
    except requests.exceptions.RequestException:
        return REQUEST_EXCEPTION

def get_definition(word, language="de"):
    print(word)
    load_dotenv(dotenv_path='Anki.env')
    base_word = get_base_form(word,language)
    print(base_word)
    answers = []

    RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
    RAPIDAPI_HOST = os.getenv('RAPIDAPI_HOST')

    url = "https://lexicala1.p.rapidapi.com/search-entries"
    querystring = {"text": base_word, "language": language, "analyzed": "true"}
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }
    result = call_api(url, headers, querystring, language)
    if(isinstance(result, tuple)):
        response_results = result[1]
        results = response_results if (isinstance(response_results, list)) else [response_results]
        for result in results:
            headwords = result["headword"] if isinstance(result["headword"], list) else [result["headword"]]
            for headword in headwords:
                if(isNoun(headword)):
                    print(f"{headword} is noun")
                else:
                    print(f"{headword} is not noun")
            print(result["senses"])

def lemmatize_fallback(word, language):
    # Check if spaCy model for the language is loaded
    if language in SPACY_MODELS:
        nlp = SPACY_MODELS[language]
        doc = nlp(word)
        for token in doc:
            return token.lemma_
    else:
        return f"spaCy model not available for language '{language}'"

def get_base_form(word, language="de"):
    # Try the API first
    lemma = lemmatize_fallback(word, language)
    return lemma

# Test words in multiple languages
get_definition("rival", "fr")
