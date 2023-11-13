from lyrics_extractor import SongLyrics
from config import GCS_API_KEY, GCS_ENGINE_ID, MUSICXMATCH_API_KEY, GENIUS_ACCESS_TOKEN
import requests
from lyricsgenius import Genius
import logging_config
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import re

logger = logging_config.logger


def azlyrics(artist, title):
    artist = (re.sub(r'[^\x00-\x7F]+', '', artist)).replace(" ", '')
    title = (re.sub(r'[^\x00-\x7F]+', '', title)).replace(" ", '')
    base_url = f"https://www.azlyrics.com/lyrics/{artist.strip().lower()}/{title.strip().lower()}.html"
    print(base_url)
    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36"
    }
    request = Request(base_url, headers=headers)
    response = urlopen(request)
    html_page = response.read()
    soup = BeautifulSoup(html_page, 'html.parser')

    html_pointer = soup.find('div', attrs={'class': 'ringtone'})
    lyrics = html_pointer.find_next('div').text.strip()
    return lyrics + f"\n\n{base_url}"


def lyricsgenius_lyrics(artist, title):
    genius = Genius(GENIUS_ACCESS_TOKEN,
                    retries=3,
                    response_format='plain',
                    verbose=False)
    song = genius.search_song(title, artist)
    lyrics = song.lyrics
    return lyrics


def lyrics_extractor_lyrics(artist, title):
    extract_lyrics = SongLyrics(GCS_API_KEY, GCS_ENGINE_ID)
    lyrics = extract_lyrics.get_lyrics(f"{title} {artist}")["lyrics"]
    return lyrics


def musicxmatch_lyrics(artist, title):
    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36"
    }
    lyrics_params = {"apikey": MUSICXMATCH_API_KEY}
    track_params = lyrics_params
    track_params["q_track"] = f"{title}"
    track_params["q_artist"] = f"{artist}"
    response = requests.get("https://api.musixmatch.com/ws/1.1/track.search",
                            params=track_params,
                            headers=headers)
    response.raise_for_status()
    logger.info(f"Response with status:{response.status_code}")
    track_data = response.json()
    try:
        track_list = track_data["message"]["body"]["track_list"]
        best_search = track_list[0]
        track_id = best_search["track"]["track_id"]
        response = requests.get(
            F"https://api.musixmatch.com/ws/1.1/track.lyrics.get?track_id={track_id}",
            params=lyrics_params)
        response.raise_for_status()
        lyrics_data = response.json()
        lyrics = lyrics_data["message"]["body"]["lyrics"]["lyrics_body"]
        return lyrics.split(
            "******* This Lyrics is NOT for Commercial use *******")[0]
    except BaseException:
        return None

 #print(azlyrics(artist="pinkpantheress", title="capable of love"))
