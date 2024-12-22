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
AUTHORIZATION_ERROR = "Authorization Error"
UNKNOWN_ERROR = "Unknown Error"
INVALID_RESPONSE = "Invalid Response"
NOUN = "Noun"
NOT_NOUN = "Not Noun"
TIMEOUT = "Timeout"
REQUEST_EXCEPTION = "Request Exception"

def isNoun(word_response):
    return word_response["results"][0]["headword"]["pos"] == "noun"

def get_article(gender, language):
    german_articles = {"feminine": "die", "masculine": "der", "neuter": "das"}
    french_articles = {"feminine": "la", "masculine": "le"}
    spanish_articles = {"feminine": "la", "masculine": "el"}

    if(language == "de"):
        return german_articles.get(gender, "unknown gender")
    if(language =="es"):
        return spanish_articles.get(gender, "unknown gender")
    if(language == "fr"):
        return french_articles.get(gender, "unknown gender")
    return "Unsupported language"

def parse_noun_data(response_data, language):
    
    headword = response_data[0].get("headword", {})
    gender = headword.get("gender", "unknown")
    article = get_article(gender, language)
    inflections = headword.get("inflections", {})

    plural_form = inflections[1].get("text") if len(inflections) > 1 else ""

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
        
        if (response.status_code == 403):
            return AUTHORIZATION_ERROR
        
        if (response.status_code != 200):
            #print(f"Request failed with status code {response.status_code}")
            return UNKNOWN_ERROR
        
        response_data = response.json()
        if not response_data["results"]:
            #print(f"No valid response for {base_word} in {language}, verify the spelling of both")
            return INVALID_RESPONSE
        
        if isNoun(response_data):
            print("it is a noun")
            parsed_data = parse_noun_data(response_data["results"], language)
            return NOUN, parsed_data
    except requests.exceptions.Timeout:
        return TIMEOUT
    except requests.exceptions.RequestException:
        return REQUEST_EXCEPTION

def get_definition(word, language="de"):
    print(word)
    load_dotenv(dotenv_path='Anki.env')
    base_word = get_base_form(word,language)
    print(base_word)

    RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
    RAPIDAPI_HOST = os.getenv('RAPIDAPI_HOST')

    url = "https://lexicala1.p.rapidapi.com/search-entries"
    querystring = {"text": base_word, "language": language, "analyzed": "true"}
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }
    result = call_api(url, headers, querystring, language)
    print(f"result is {result}")
    
        


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
get_definition("klein", "de")
