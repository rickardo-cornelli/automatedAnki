import requests
import os
from dotenv import load_dotenv


# Load API key from the environment file
load_dotenv("../Anki.env")

# Load environment variables from Anki.env
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Anki.env")
load_dotenv(env_path)

IMAGES_DIR = "media/images"

FETCH_REQUEST_EXCEPTION = "An error occured while trying to fetch the image"
DOWNLOAD_REQUEST_EXCEPTION = "An error occured while trying to download the image"

if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)

def get_pixabay_api_key():
    return os.getenv("PIXABAY_KEY")

def image_file_exists(file_path):
    return os.path.exists(file_path)


def fetch_pixabay_images(query, api_key,lang):
    
    if (not api_key):
        print("Error: Pixabay API key not found in Anki.env.")
        return
    
    base_url = "https://pixabay.com/api/"
    params = {
        "key": api_key,
        "q": query,  # No need to encode manually; `requests` does it.
        "image_type": "photo",
        "lang" : lang,
        "per_page": 5,  # Fetch up to 5 images
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        # Check total hits and extract image URLs
        if (int(data.get("totalHits", 0)) > 0):
            return [hit["previewURL"] for hit in data["hits"]]
        else:
            return []
    except requests.exceptions.RequestException as e:
        return FETCH_REQUEST_EXCEPTION
    
def download_image(image_url, save_path):
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()

        with open(save_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        
    except requests.RequestException:
        return DOWNLOAD_REQUEST_EXCEPTION




def get_image(word, language="en"):
    file_path = os.path.join(IMAGES_DIR, f"{word.replace(' ', '_')}.jpg")

    api_key = get_pixabay_api_key()
    if (not image_file_exists(file_path)):
        image_urls = fetch_pixabay_images(word, api_key, "de")

        if (not image_urls):
            print(f"No image found for {word}")
            return
        else:
        # Download the first image from the list
            first_image_url = image_urls[0]
            download_image(first_image_url, file_path)
    return {"filename": f"{word}.jpg", "filepath": file_path}
