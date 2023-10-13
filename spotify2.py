import spotipy
# from spotipy import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET
from logging import basicConfig, getLogger, INFO, FileHandler, StreamHandler
import json
# import logging
basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(lineno)d | %(message)s',
            handlers=[FileHandler('Z_Logs.txt'), StreamHandler()], level=INFO)
## In main
logger = getLogger(__name__)
# basicConfig(level=INFO, filename='logs.txt', format='%(asctime)s - %(name)s -  %(levelname)s - %(message)s ')
   
# logger = getLogger(__name__)
class Spotify():
    SPOTIPY_CLIENT_ID = SPOTIPY_CLIENT_ID
    SPOTIPY_CLIENT_SECRET = SPOTIPY_CLIENT_SECRET
    SCOPE = "playlist-modify-private"
    TOKEN_CACHE_PATH = "token.txt"

    def __init__(self) -> None:
        # # Authorization 
        # self.spotify = Spotify(client_credentials_manager=SpotifyClientCredentials())

        self.sp = spotipy.Spotify(
                auth_manager=SpotifyOAuth(
                scope=self.SCOPE,
                redirect_uri="http://example.com",
                client_id=self.SPOTIPY_CLIENT_ID,
                client_secret= self.SPOTIPY_CLIENT_SECRET,
                show_dialog=True,
                cache_path=self.TOKEN_CACHE_PATH
            )
        )

        # # Authorization 2
        self.scope = "playlist-modify-public"
        self.no_of_songs = 5        

    def get_artist_albums(self,artist_id, type):
        # Get artist albums information
        artist_albums_information = self.sp.artist_albums(artist_id, album_type=type)               
        # Extract album names and URIs from each item
        artist_albums_info = [{'name': album['name'], 'uri': album['uri']} for album in artist_albums_information['items']]
        artist_albums = []
        for album in enumerate(artist_albums_info):
            artist_albums.append(album)
        list_of_albums = []
        for item in artist_albums:
            dict = {
                'index': item[0],
                "name" : item[1]["name"],
                "uri": item[1]["uri"]
            }
            list_of_albums.append(dict)
        return list_of_albums

    def artist(self, name) -> dict:
        artist_data = self.sp.search(name, type='artist')
        """Get all possible details of an artist"""
        logger.info("Getting artist ...")
        possible_artists = artist_data["artists"]["items"]
        if len(possible_artists)==0:
            logger.error("No artist found")
            return None
        most_popular = sorted(possible_artists, key=lambda person: person["popularity"], reverse=True)
        chosen_artist = None
        # TODO: Error handling 
        chosen_artist = most_popular[0]
        print("Chosen is",chosen_artist["name"])
        images_data = chosen_artist["images"]

        # return self.top_songs,self.top_tracks['tracks'][:no_of_tracks]
        artist_details =  {
                'uri':chosen_artist["uri"],
                'followers': chosen_artist["followers"]["total"],
                'images': [item["url"] for item in images_data][0],
                'name':chosen_artist["name"],
                'genres': chosen_artist["genres"],
                }
        top_tracks = self.sp.artist_top_tracks(artist_details["uri"])
        top_tracks_list = top_tracks['tracks'][:self.no_of_songs]
        artist_details['top_songs'] = [track['name'] for track in top_tracks_list]
        artist_albums = self.sp.artist_albums(artist_details['uri'], album_type='album')
        artist_details['albums'] = artist_albums['items']
        return artist_details
    
    def track(self, artist, title) -> dict:
        """Get all possible details of an track"""
        track_data = self.sp.search(q=f"artist: '{artist}' track:'{title}'", type="track")
        logger.info("Getting track info ...")
        possible_tracks = track_data["tracks"]["items"]
        if len(possible_tracks) == 0:
            logger.info("No tracks found")
            return
        # return json.dumps(possible_tracks[0], indent=4)
        chosen_song = possible_tracks[0]
        track_details = {
            'id': chosen_song["id"],
            'artists':[artist["name"] for artist in chosen_song["album"]["artists"]],
            'name': chosen_song["name"],
            'album': chosen_song["album"]["name"],
            'release_date': chosen_song["album"]["release_date"],
            'total_tracks': chosen_song["album"]["total_tracks"],
            'track_no': chosen_song["track_number"],
            'uri': chosen_song["uri"],
            'preview_url': chosen_song["preview_url"],            
            'external_urls': chosen_song["external_urls"]["spotify"],            
            'duration_ms': chosen_song["duration_ms"],            
            'explicit': chosen_song["explicit"],            
        }
        if chosen_song.get('album') and chosen_song['album'].get('images'):
            track_details['image'] = chosen_song['album']['images'][0]['url']
        else:
            track_details['image'] =  "https://cdn.business2community.com/wp-content/uploads/2014/03/Unknown-person.gif"
            logger.info(f"No image found for track {track_details['name']}")
        
        return track_details     

    def album(self, artist, title) -> dict:
    # Get album tracks information
        album_data = self.sp.search(q=f"{title}' {artist}", type="album")
        possible_albums = album_data["albums"]["items"]
        if len(possible_albums) == 0:
            logger.info("No tracks found")
            return
        # return json.dumps(possible_tracks[0], indent=4)
        chosen_album = possible_albums[0]
        album_details = {
            'id': chosen_album["id"],
            'artists':[artist["name"] for artist in chosen_album["artists"]],
            'name': chosen_album["name"],
            'release_date': chosen_album["release_date"],
            'total_tracks': chosen_album["total_tracks"],
            'uri': chosen_album["uri"],
        }
        items = self.sp.album_tracks(album_details["id"])["items"]
        album_details['album_tracks'] = {"name":[item["name"] for item in items]}
        return json.dumps(album_details, indent=4)

# logger.info("Message")
spotify = Spotify()
print(json.dumps(spotify.artist("Maggie Lindemann")))

# print(spotify.track("Tate Mcrae", "You"))
# print(spotify.album("ELIO", "ELIO'S INFERNO"))
# with open("data.txt", 'w') as file:
#     file.write(spotify.album("ELIO", "ELIO'S INFERNO"))
# logger.info("saved to file")
