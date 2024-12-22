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

def call_api(url, headers, querystring):
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
        
        return NOUN if isNoun(response_data) else NOT_NOUN

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
    querystring = {"text": base_word, "language": "language", "analyzed": "true"}
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }
    result = call_api(url, headers, querystring)
    
        


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
get_definition("hursm", "sv")
