import spotipy
# from spotipy import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET
from logging import basicConfig, getLogger, INFO
import json
# import logging
basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=INFO  # Set the desired log level (INFO, DEBUG, ERROR, etc.)
)
## In main
logger = getLogger(__name__)
# basicConfig(level=INFO, filename='logs.txt', format='%(asctime)s - %(name)s -  %(levelname)s - %(message)s ')
   
# logger = getLogger(__name__)
class Spotify():
    def __init__(self) -> None:
        self.SPOTIPY_CLIENT_ID  = SPOTIPY_CLIENT_ID
        self.SPOTIPY_CLIENT_SECRET  = SPOTIPY_CLIENT_SECRET
        # # Authorization 
        # self.spotify = Spotify(client_credentials_manager=SpotifyClientCredentials())

        self.sp = spotipy.Spotify(
                auth_manager=SpotifyOAuth(
                scope="playlist-modify-private",
                redirect_uri="http://example.com",
                client_id=self.SPOTIPY_CLIENT_ID,
                client_secret= self.SPOTIPY_CLIENT_SECRET,
                show_dialog=True,
                cache_path="token.txt"
            )
        )

        # # Authorization 2
        self.scope = "playlist-modify-public"
        self.no_of_songs = 5

        # Artist

    def artist(self, name:str):
        artist_data = self.sp.search(name, type='artist')
        """Get all possible details of an artist"""
        logger.info("Getting artist ...")
        artist_list = artist_data["artists"]["items"]
        if len(artist_list)==0:
            logger.error("No artist found")
        most_popular = sorted(artist_list, key=lambda person: person["popularity"], reverse=True)
        chosen_artist = None
        # TODO: Error handling 
        chosen_artist = most_popular[0]
        print("Chosen is",chosen_artist["name"])
        images_data = chosen_artist["images"]

        # return self.top_songs,self.results['tracks'][:no_of_tracks]
        artist_details =  {
                'uri':chosen_artist["uri"],
                'followers': chosen_artist["followers"]["total"],
                'images': [item["url"] for item in images_data],
                'name':chosen_artist["name"],
                'genres': chosen_artist["genres"],
                'top_songs': None
                }
        results = self.sp.artist_top_tracks(artist_details["uri"])
        top_tracks_list = results['tracks'][:self.no_of_songs]
        artist_details['top_songs'] = [track['name'] for track in top_tracks_list]
        return json.dumps(artist_details, indent=3)

logger.info("Message")
spotify = Spotify()
print(spotify.artist("Selena Gomez"))
