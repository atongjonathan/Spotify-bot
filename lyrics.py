import requests
import html,os
from lyrics_extractor import SongLyrics
GCS_ENGINE_ID = os.getenv("GCS_ENGINE_ID")
GCS_API_KEY = os.getenv("GCS_API_KEY")
query = "People you know by Selena Gomez"
def get_lyrics(query):
    """Gets the title, thumbnail, releaseDate, artist, coverImage, genius link of a song query"""
    base_url = f"https://api.safone.me/lyrics?query={query}"
    query.replace(" ", "%20")
    response = requests.get(base_url)
    response.raise_for_status()
    data = response.json()
    try:
        lyrics = data["lyrics"]
    except KeyError:
        return {"lyrics": "Not found", "releaseDate" : "None"}
    with open("lyrics.txt", 'w', encoding="cp437", errors="ignore") as file:
        file.write(lyrics)
    with open("lyrics.txt", encoding="cp437", errors="ignore") as file:
        data_list = file.readlines()[1:-1]
        new_data = "".join((html.unescape(data_list)))
    data["lyrics"] = new_data
    os.remove("lyrics.txt")
    return data

extract_lyrics = SongLyrics(GCS_API_KEY, GCS_ENGINE_ID)
