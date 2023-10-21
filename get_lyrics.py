from lyrics_extractor import SongLyrics
from config import GCS_API_KEY, GCS_ENGINE_ID, MUSICXMATCH_API_KEY
import requests

def lyrics_extractor_lyrics(artist,title):
    extract_lyrics = SongLyrics(GCS_API_KEY, GCS_ENGINE_ID)
    lyrics = extract_lyrics.get_lyrics(f"{title} {artist}")["lyrics"]
    return lyrics

def musicxmatch_lyrics(artist, title):
    headers = headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36"}
    lyrics_params = {
        "apikey": MUSICXMATCH_API_KEY
    }
    track_params = lyrics_params
    track_params["q_track"] =  f"{title}"
    track_params["q_artist"] =  f"{artist}"
    response = requests.get("https://api.musixmatch.com/ws/1.1/track.search", params=track_params, headers=headers)
    response.raise_for_status()
    track_data = response.json()
    track_list = track_data["message"]["body"]["track_list"]
    best_search = track_list[0]
    track_id = best_search["track"]["track_id"]
    response = requests.get(F"https://api.musixmatch.com/ws/1.1/track.lyrics.get?track_id={track_id}", params=lyrics_params)
    response.raise_for_status()
    lyrics_data = response.json()
    lyrics = lyrics_data["message"]["body"]["lyrics"]["lyrics_body"]
    return lyrics.split("******* This Lyrics is NOT for Commercial use *******")[0]

