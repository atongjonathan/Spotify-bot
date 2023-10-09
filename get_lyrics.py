import os
from lyrics_extractor import SongLyrics
from config import GCS_API_KEY, GCS_ENGINE_ID
from config import GENIUS_ACCESS_TOKEN
from lyricsgenius import Genius

# def get_lyrics_extractor(query):
#     extract_lyrics = SongLyrics(GCS_API_KEY, GCS_ENGINE_ID)
#     lyrics = extract_lyrics.get_lyrics(query)
#     return lyrics

def get_lyrics_genius(artist,title) -> str:
    genius = Genius(GENIUS_ACCESS_TOKEN)
    # genius_artist = genius.search_artist(artist)
    song = genius.search_song(title,artist)
    lyrics = song.lyrics.replace('Embed', '').replace("Contributors", '')
    lyrics = lyrics.split("Lyrics")[1]
    return lyrics
