from pytube import YouTube
import os
import re
from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, ID3
from moviepy.editor import AudioFileClip
import requests
import urllib.request
from spotify import spotify

def get_yt_url(query):
    query = query.replace(" ", "+")
    base_url = "https://www.youtube.com/results?search_query="
    response = urllib.request.urlopen(f"{base_url}{query}")
    soup = response.read().decode()
    search_results = re.findall(r"watch\?v=(\S{11})", soup)
    best_id = search_results[0]
    first_video = f"https://www.youtube.com/watch?v={best_id}"
    return first_video
def download_webm(vid_url):
    yt =YouTube(vid_url, allow_oauth_cache=True, use_oauth=True)
    itag = yt.streams.filter(only_audio=True, abr="160kbps").first().itag
    print(itag)
    audio = yt.streams.get_by_itag(itag).download()
    base = os.path.splitext(audio)[0]
    audio_file = base + ".mp3"
    mp4_no_frame = AudioFileClip(audio)
    mp4_no_frame.write_audiofile(audio_file, logger=None)
    mp4_no_frame.close()
    os.remove(audio)
    # os.replace(audio_file, f"../music/tmp/{yt.title}.mp3")
    # audio_file = f"../music/tmp/{yt.title}.mp3"
    print("Success")
    return audio_file

def get_track_info(track_url):
    res = requests.get(track_url)
    if res.status_code != 200:
        raise ValueError("Invalid Spotify track URL")

    track = spotify.track(track_url)

    track_metadata = {
        "artist_name": track["artists"][0]["name"],
        "track_title": track["name"],
        "track_number": track["track_number"],
        "isrc": track["external_ids"]["isrc"],
        "album_art": track["album"]["images"][1]["url"],
        "album_name": track["album"]["name"],
        "release_date": track["album"]["release_date"],
        "artists": [artist["name"] for artist in track["artists"]],
    }

    return track_metadata
def set_metadata(metadata, file_path):
    """adds metadata to the downloaded mp3 file"""

    mp3file = EasyID3(file_path)

    # add metadata
    mp3file["albumartist"] = metadata["artist_name"]
    mp3file["artist"] = metadata["artists"]
    mp3file["album"] = metadata["album_name"]
    mp3file["title"] = metadata["track_title"]
    mp3file["date"] = metadata["release_date"]
    mp3file["tracknumber"] = str(metadata["track_number"])
    mp3file["isrc"] = metadata["isrc"]
    mp3file.save()

    # add album cover
    audio = ID3(file_path)
    with urllib.request.urlopen(metadata["album_art"]) as albumart:
        audio["APIC"] = APIC(
            encoding=3, mime="image/jpeg", type=3, desc="Cover", data=albumart.read()
        )
    audio.save(v2_version=3)

