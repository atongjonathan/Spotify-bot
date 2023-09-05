import requests
import html,os
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
        return None
    with open("lyrics.txt", 'w', encoding="cp437", errors="ignore") as file:
        file.write(lyrics)
    with open("lyrics.txt", encoding="cp437", errors="ignore") as file:
        data_list = file.readlines()[1:-1]
        new_data = "".join((html.unescape(data_list)))
    data["lyrics"] = new_data
    os.remove("lyrics.txt")
    return data
