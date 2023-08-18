import spotipy
from spotipy import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
from top_songs import get_data
import json,os

SPOTIPY_CLIENT_ID  = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET  = os.getenv('SPOTIPY_CLIENT_SECRET')
# # Authorization 
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

# # Authorization 2
scope = "playlist-modify-public"

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="http://example.com",
        client_id=SPOTIPY_CLIENT_ID,
        client_secret= SPOTIPY_CLIENT_SECRET,
        show_dialog=True,
        cache_path="token.txt"
    )
)
no_of_songs = 5

top_songs = []
def artist_top_tracks(uri, no_of_tracks):
    results = spotify.artist_top_tracks(uri)
    for track in results['tracks'][:no_of_tracks]:
        track_name = track['name']
        top_songs.append(track_name)
    return top_songs,results['tracks'][:no_of_tracks]

  
def get_ids(dict_of_songs:dict):
    all_ids = []
    for track_dict in dict_of_songs:
        artist = track_dict["artist"]
        track = track_dict["track"]
        best_song_id = get_track_id(artist,track)
        all_ids.append(best_song_id)
    return all_ids


# Artist details❤
def get_details_artist(name:str):
    artists_results = spotify.search(q=name, type="artist")
    artist_details = artists_results["artists"]["items"][0]
    uri = artist_details["uri"]
    followers = artist_details["followers"]["total"]
    images_data = artist_details["images"]
    images = [item["url"] for item in images_data]
    name = artist_details["name"]
    genres = artist_details["genres"]
    return uri,followers,images,name,genres


# Search for a track
def get_track_id(artist:str,track:str):
    best_song = spotify.search(q=f"{artist}, {track}", type='track')
    best_song_id = best_song["tracks"]["items"][0]["id"]
    return best_song_id


# # Create a playlist and add tracks
def create_playlist(all_ids):
    playlist = sp.user_playlist_create(name="Olivia Rodrigo Vampire playlist", description="Testing Spotipy app",user="0rcm19m6sa0i20keycezqykyj",public=True)
    playlist_id = playlist
    # Add tracks
    sp.user_playlist_add_tracks(user="0rcm19m6sa0i20keycezqykyj",playlist_id="41ZEbDPBl5OERQNEANqTLc",tracks=all_ids)
    return playlist_id

# Get user's saved tracks
def get_my_saved_tracks():
    all_saved = []
    results = sp.current_user_saved_tracks()
    for idx, item in enumerate(results['items']):
        track = item['track']
        index = idx
        artist_name = track['artists'][0]['name']
        track_name = track['name']
        item = {
            "index": index,
            "artist_name": artist_name,
            "track_name": track_name
        }
        all_saved.append(item)
    return all_saved

def get_track_image(track_id):
    # Get track information
    track_info = sp.track(track_id)

    # Get the cover art URL
    if track_info.get('album') and track_info['album'].get('images'):
        image = track_info['album']['images'][0]['url']
        return image
    else:
        return None

def get_track_details(track_id):
    track_info = sp.track(track_id)
    artist = track_info["album"]["artists"][0]["name"]
    album = track_info["album"]["name"]
    release_date = track_info["album"]["release_date"]
    total_tracks = track_info["album"]["total_tracks"]
    track_no = track_info["track_number"]
    uri = track_info["uri"]
    preview_url = track_info["preview_url"]

    return artist, preview_url, release_date, album, track_no,total_tracks

def get_albums(uri):
    albums = []
    results = spotify.artist_albums(uri, album_type='album')
    albums = results['items']
    return albums

def get_album_tracks(album_id):
    # Get album tracks information
    album_tracks_info = sp.album_tracks(album_id)
    
    # Extract track information from each item
    track_list = []
    for track in album_tracks_info['items']:
        track_name = track['name']
        track_id = track['id']
        track_list.append({'name': track_name, 'id': track_id})
    
    return track_list

def get_artist_albums(artist_id):
    # Get artist albums information
    artist_albums_info = sp.artist_albums(artist_id, album_type='album')
    
    # Extract album names and URIs from each item
    albums = [{'name': album['name'], 'uri': album['uri']} for album in artist_albums_info['items']]
    
    return albums

def get_album_cover_art(album_uri):
    # Extract album ID from the URI
    album_id = album_uri.split(':')[-1]
    
    # Get album information
    album_info = sp.album(album_id)
    release_date = album_info['release_date']
    total_tracks = album_info['total_tracks']
    cover_art_url = album_info['images'][0]['url']
    
    return release_date,total_tracks,cover_art_url
# print(get_albums("spotify:artist:4dpARuHxo51G3z768sgnrY")[0]['name'])