import requests
import base64
# URL for AnkiConnect
ANKI_CONNECT_URL = "http://localhost:8765"

# used to transfer an audio file to the local anki client
def store_audio_file(filename, file_path):
    with open(file_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")

    request = {
        "action": "store#MediaFile",
        "version": 6,
        "params": {
            "filename": filename,
            "data": data
        }
    }
    response = requests.post(ANKI_CONNECT_URL, json=request)
    return response.json()

def add_card(card):
   
    payload = {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": card
        }
    }
    response = requests.post(ANKI_CONNECT_URL, json=payload)
    response.raise_for_status()  # Raise an exception for HTTP errors
    result = response.json()
    if result.get("error"):
        raise Exception(f"Error adding card: {result['error']}")
    return result.get("result", "Card added successfully")


def add_cards_in_batch(cards):
    results = []
    for card in cards:
        try:
            result = add_card(card)
            results.append(result)
        except Exception as e:
            print(f"Error adding card: {e}")
            results.append(None)  # Track failed cards
    return results