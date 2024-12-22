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

def isNoun(word_response):
    return word_response["results"][0]["headword"]["pos"] == "noun"

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

    response = requests.get(url, headers=headers, params=querystring, timeout=10)
    if(response.status_code == 200):
        response_data = response.json()

        if response_data["results"]:
            if(isNoun(response_data)):
                print(f"{base_word} is a noun")
            else:
                print(f"{base_word} is not a noun")
        else:
            print(f"No valid response for {base_word} in {language}, verify the spelling of both")
    elif(response.status_code == 403):
        print("Status code 403, verify that you have set up your API key correctly")
    else:
        print(f"Request failed with status code {response.status_code}")
    return None  # Indicate failure


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
