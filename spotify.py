import spotipy
from spotipy import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
from top_songs import get_data
import os

SPOTIPY_CLIENT_ID  = "769ae67cd8f94d9b8e8a8bdac6ad48c3" #os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET  = "856a8a2f558e4f15b2236761ebd3a1a3"#os.getenv('SPOTIPY_CLIENT_SECRET')
# SPOTIPY_REDIRECT_URI   = os.getenv('SPOTIPY_REDIRECT_URI' )

# # Authorization 
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET))

# # Authorization 2
scope = "playlist-modify-public"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,
                        client_id= SPOTIPY_CLIENT_ID,
                        client_secret=SPOTIPY_CLIENT_SECRET,
                        redirect_uri="http://example.com",
                        show_dialog=True,
                        cache_path="token.txt"))


no_of_songs = 10

top_songs = []
def get_cover_art(uri, no_of_tracks):
    results = spotify.artist_top_tracks(uri)
    for track in results['tracks'][:no_of_tracks]:
        track_name = track['name']
        cover_art = track['album']['images'][0]['url']
        top_songs.append([track_name,cover_art])
    return top_songs,results['tracks'][:no_of_tracks]


def get_dic_of_songs(no_of_songs,url):
    titles,artists = get_data(url, no_of_songs)
    dict_of_songs = []
    for number in range(0,no_of_songs):
        song = {
            "artist": artists[number],
            "track": titles[number]
        }
        dict_of_songs.append(song) 
    return dict_of_songs  



# Artist details❤
def get_details_artist(name:str):
    artists_results = spotify.search(q=name, type="artist")
    artist_details = artists_results["artists"]["items"][0]
    return artist_details
# print(get_details_artist("Selena Gomez")["uri"])

def get_artist_image(name:str):
    # if len(sys.argv) > 1:
    #     name = ' '.join(sys.argv[1:])
    # else:
    #     name = 'Radiohead'

    results = spotify.search(q=f"{name}", type='artist')
    items = results['artists']['items']
    if len(items) > 0:
        artist = items[0]
        artist_name = artist['name']
        image = artist['images'][0]['url']

        return image

# Search for a track
def search_song_id(artist:str,track:str):
    best_song = spotify.search(q=f"{artist}, {track}", type='track')
    best_song_id = best_song["tracks"]["items"][0]["id"]
    return best_song_id



def get_ids(dict_of_songs:dict):
    all_ids = []
    for track_dict in dict_of_songs:
        artist = track_dict["artist"]
        track = track_dict["track"]
        best_song_id = search_song_id(artist,track)
        all_ids.append(best_song_id)
    return all_ids


# # Create a playlist and add tracks
def create_playlist(all_ids):
    playlist = sp.user_playlist_create(name="Olivia Rodrigo Vampire playlist", description="Testing Spotipy app",user="0rcm19m6sa0i20keycezqykyj",public=True)
    playlist_id = playlist
    # Add tracks
    sp.user_playlist_add_tracks(user="0rcm19m6sa0i20keycezqykyj",playlist_id="41ZEbDPBl5OERQNEANqTLc",tracks=all_ids)
    return playlist_id

# Get user's saved tracks
def get_saved_tracks():
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
def get_preview_url(id):
    track_info = sp.track(id)
    url = track_info['preview_url']
    return url

def get_track_coverart(track_id):
    # Get track information
    track_info = sp.track(track_id)

    # Get the cover art URL
    if track_info.get('album') and track_info['album'].get('images'):
        coverart_url = track_info['album']['images'][0]['url']
        return coverart_url
    else:
        return None
# image = get_track_coverart("42VsgItocQwOQC3XWZ8JNA")
# print(image)