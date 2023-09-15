from pytube import YouTube
import os
import re
from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, ID3, USLT
from moviepy.editor import AudioFileClip
import urllib.request
import yt_dlp

options = {
    "format" : "bestaudio/best"
}
ytdl = yt_dlp.YoutubeDL(options)
# ytdl(options)

def get_yt_url(query):
    # Define a regular expression pattern to match non-English letters
    non_english_pattern = re.compile(r'[^\x00-\x7F]+')
    # Replace non-English letters with an empty string
    cleaned_string = non_english_pattern.sub('', query)
    # Decode the encoded string to get a printable string
    query = cleaned_string.replace(" ", "%20")
    base_url = "https://www.youtube.com/results?search_query="
    response = urllib.request.urlopen(f"{base_url}{query}")
    soup = response.read().decode()
    search_results = re.findall(r"watch\?v=(\S{11})", soup)
    for url in (search_results[:5]):
        yt_base = f"https://www.youtube.com/watch?v={url}"
        yt = YouTube(yt_base)
        if yt.length < 100:
            pass
        else:
            best_uri = url    
    return f"https://www.youtube.com/watch?v={best_uri}"
def download_webm(vid_url, title):
    ytdl.download([vid_url])
    for file in os.listdir("."):
        if os.path.isfile(file) and file.endswith(".webm"):
            audio = file
            break 
    base = os.path.splitext(audio)[0]
    audio_file = base + ".mp3"
    mp4_no_frame = AudioFileClip(audio)
    mp4_no_frame.write_audiofile(audio_file, logger=None)
    mp4_no_frame.close()
    os.remove(audio)
    os.replace(audio_file, f"{title}.mp3")
    audio_file = f"{title}.mp3"
    return audio_file

def set_metadata(albumartist,artist,album,title,date,tracknumber,photo,file_path):
    """adds metadata to the downloaded mp3 file"""

    mp3file = EasyID3(file_path)

    # add metadata
    mp3file["albumartist"] = albumartist
    mp3file["artist"] = artist
    mp3file["album"] = album
    mp3file["title"] = title
    mp3file["date"] = date
    mp3file["tracknumber"] = str(tracknumber)
    mp3file["tracknumber"] = "@JonaAtong"
    mp3file.save()

    # add album cover
    audio = ID3(file_path)
    with urllib.request.urlopen(photo) as albumart:
        audio["APIC"] = APIC(
            encoding=3, mime="image/jpeg", type=3, desc="Cover", data=albumart.read()
        )
    # Create a USLT frame with lyrics

    # Add the USLT frame to the ID3 tags
    audio.save(v2_version=3)

