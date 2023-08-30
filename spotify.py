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
no_of_songs = 10

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
    name = name.lower()
    artists_results = spotify.search(q=name, type="artist")
    artist_list = artists_results["artists"]["items"]
    sorted_persons = sorted(artist_list, key=lambda person: person["popularity"], reverse=True)
    for artist in sorted_persons:
        if name in str(artist["name"]).lower():
            chosen_artist = artist
            break
    uri = chosen_artist["uri"]
    followers = chosen_artist["followers"]["total"]
    images_data = chosen_artist["images"]
    images = [item["url"] for item in images_data]
    name = chosen_artist["name"]
    genres = chosen_artist["genres"]
    return uri,followers,images,name,genres


# Search for a track
def get_track_id(artist:str,track:str):
    data = spotify.search(q=f"artist: '{artist[:20]}' track:'{track}'", type="track")
    songs = data["tracks"]["items"]
    chosen_song = songs[0]
    # for song in songs:
    #     if track in song['name']:
    #         chosen_song = song
    #         break
    #     else:
    #         print(track in song['name'], song['name'])
    return chosen_song["id"]


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

def get_artist_albums(artist_id, type):
    # Get artist albums information
    artist_albums_information = sp.artist_albums(artist_id, album_type=type)
    
    
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

def get_top_tracks(uri):
    top_tracks_data = artist_top_tracks(uri, 10)
    titles_list = top_tracks_data[0]
    track_details = []
    tracks_data = top_tracks_data[1]
    for track in tracks_data:
        uri = track["uri"]
        artist, preview_url, release_date, album, track_no,total_tracks = get_track_details(uri)
        dict = {
            "artist":artist,
            "name":track["name"],
            "preview_url": preview_url,
            "image": get_track_image(uri),
            "release_date": release_date,
            "album": album,
            'track_no':track_no,
            "total_tracks":total_tracks
        }
        track_details.append(dict)
def get_artist_eps(artist_id):
    eps = []

    artist_albums = sp.artist_albums(artist_id, album_type='single')
    for album in artist_albums['items']:
        album_type = album['album_type']
        if album_type == 'single':
            eps.append(album["name"])

    return eps

