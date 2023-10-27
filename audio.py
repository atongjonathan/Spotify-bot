from pytube import YouTube
import os
import re
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
import urllib.request
import googleapiclient.discovery
import os
from config import YOUTUBE_API_KEY
import yt_dlp
import eyed3
from eyed3.id3.frames import ImageFrame


options = {
    "format" : "bestaudio[ext=mp3]/bestaudio/best"
}
ytdl = yt_dlp.YoutubeDL(options)
# Define your API key and service name
# api_key = "YOUR_API_KEY"
api_service_name = "youtube"
api_version = "v3"

# Create a YouTube API client
youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=YOUTUBE_API_KEY)




class Audio():
    def search(sself, search_query):# Define your search query
    # Perform the search
        search_response = youtube.search().list(
            q=search_query,
            type="video",
            part="id",
            maxResults=10  # You can adjust the number of results you want to retrieve
        ).execute()

        # Extract the video IDs from the search results
        video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
        vid_id = video_ids[0]

        url = f"https://www.youtube.com/watch?v={vid_id}"
        return url


    def download_webm(self, url):
        ytdl.download([url])
        return True

    def set_metadata(self, track_details, file_path):
        """adds metadata to the downloaded mp3 file"""
        artist = track_details["artists"][0]
        album_artist = artist
        date = track_details["release_date"]
        album = track_details["album"]
        title = track_details["name"]
        track_number = track_details["name"]
        image = track_details["image"]
        audio = MP3(file_path, ID3=ID3)
        try:
            audio.add_tags()
        except error:
            pass
        audio.tags.add(APIC(mime='image/jpeg',type=3,desc=u'Cover',data=open(image,'rb').read()))
        # edit ID3 tags to open and read the picture from the path specified and assign it
        audio.save() 
        return audio

# save the changes

