from pytube import YouTube
import os
import re
from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, ID3
import urllib.request

class Audio():
    def download_webm(self,query,title):
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
            if yt.length < 100 or yt.length > 300:
                pass
            else:
                best_uri = url
        vid_url = best_uri 
        for file in os.listdir("."):
            if os.path.isfile(file) and file.endswith(".mp3"):
                return file
        return None
        

    def set_metadata(albumartist,artist,date,album,title,tracknumber,photo,file_path):
        """adds metadata to the downloaded mp3 file"""
        mp3file = EasyID3(file_path)
        # add metadata
        mp3file["albumartist"] = artist
        mp3file["artist"] = artist
        mp3file["album"] = album
        mp3file["title"] = title
        mp3file["date"] = date
        mp3file["tracknumber"] = str(tracknumber)
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
        return audio

