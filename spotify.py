import spotipy
from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET
from spotipy.oauth2 import SpotifyClientCredentials
import json
from logging import getLogger
logger = getLogger(__name__)


class Spotify():
    SPOTIPY_CLIENT_ID = SPOTIPY_CLIENT_ID
    SPOTIPY_CLIENT_SECRET = SPOTIPY_CLIENT_SECRET
    SCOPE = "playlist-modify-private"
    TOKEN_CACHE_PATH = "token.txt"

    def __init__(self) -> None:
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID,
                                                                        client_secret=SPOTIPY_CLIENT_SECRET))

    def get_chosen_artist(self, uri):
        chosen_artist = self.sp.artist(uri)
        images_data = chosen_artist["images"]
        artist_details = {
            'uri': chosen_artist["uri"],
            'followers': chosen_artist["followers"]["total"],
            'images': [item["url"] for item in images_data][0],
            'name': chosen_artist["name"],
            'genres': [genre.title() for genre in chosen_artist["genres"]],
        }
        top_tracks = self.sp.artist_top_tracks(artist_details["uri"])['tracks']
        artist_details['top_songs'] = [
            {"name": track['name'], "uri":track['uri'], "artist_uri": track["album"]["artists"][0]["uri"]} for track in top_tracks]
        artist_details = self.additional_details(artist_details)
        return artist_details

    def artist(self, name: str) -> list:
        """Get all possible details of an artist"""
        name = name.lower()
        artist_data = self.sp.search(name, type='artist')
        possible_artists = artist_data["artists"]["items"]
        if len(possible_artists) == 0:
            logger.error("No artist found")
            return None
        most_popular = sorted(
            possible_artists,
            key=lambda person: person["popularity"],
            reverse=True)
        artist_results = []
        for artist in most_popular:
            if name in str(artist["name"]).lower():
                artist_results.append(artist)

        artists_data = []
        for artist in artist_results:
            artist_details = {
                'uri': artist["uri"],
                'name': artist["name"],
                'followers': f'{artist["followers"]["total"]:,}'
            }
            artists_data.append(artist_details)
        return artists_data

    def additional_details(self, artist_details):
        types = ["album", "single", "compilation"]
        for one_type in types:
            key = f"artist_{one_type}s"
            artist_details[f"{key}"] = self.sp.artist_albums(
                artist_details['uri'], album_type=f'{one_type}')
            artist_details[f"{key}"] = (artist_details[f"{key}"]["items"])
            artist_details[key] = {
                f"{one_type}": [
                    {
                        "artist_uri": artist_details["uri"],
                        "name": item['name'],
                        "uri":item['uri']} for item in artist_details[key]]}
        return artist_details

    def get_chosen_song(self, uri):
        chosen_song = self.sp.track(uri)
        track_details = {
            'id': chosen_song["id"],
            'artists': [artist["name"] for artist in chosen_song["album"]["artists"]],
            'name': chosen_song["name"],
            'album': chosen_song["album"]["name"],
            'release_date': chosen_song["album"]["release_date"],
            'total_tracks': chosen_song["album"]["total_tracks"],
            'track_no': chosen_song["track_number"],
            'uri': chosen_song["uri"],
            'preview_url': chosen_song["preview_url"],
            'external_url': chosen_song["external_urls"]["spotify"],
            'duration_ms': chosen_song["duration_ms"],
            'explicit': chosen_song["explicit"],
        }
        if chosen_song.get('album') and chosen_song['album'].get('images'):
            track_details['image'] = chosen_song['album']['images'][0]['url']
        else:
            track_details['image'] = "https://cdn.business2community.com/wp-content/uploads/2014/03/Unknown-person.gif"
            logger.info(f"No image found for track {track_details['name']}")

        return track_details

    def song(self, artist, title) -> list:
        """Get all possible details of an track"""
        track_data = self.sp.search(q=f"{artist} {title}", type="track")
        possible_tracks = track_data["tracks"]["items"]
        track_results = []
        if len(possible_tracks) == 0:
            logger.info(f"No tracks found for {artist}, {title}")
            return
        for track in possible_tracks:
            track_details = {
                'artists': ', '.join([artist["name"] for artist in track["album"]["artists"]]),
                'name': track["name"],
                'uri': track["uri"]
            }
            track_results.append(track_details)
        return track_results

    def album(self, artist, title, uri) -> dict:
        if uri is not None:
            try:
                chosen_album = self.sp.album(uri)
            except BaseException:
                return uri
        else:
            album_data = self.sp.search(q=f"{title}' {artist}", type="album")
            possible_albums = album_data["albums"]["items"]
            if len(possible_albums) == 0:
                logger.info("No tracks found")
                return
            # return json.dumps(possible_tracks[0], indent=4)
            chosen_album = possible_albums[0]
        album_details = {
            'id': chosen_album["id"],
            'artists': [artist["name"] for artist in chosen_album["artists"]],
            'name': chosen_album["name"],
            'release_date': chosen_album["release_date"],
            'total_tracks': chosen_album["total_tracks"],
            'uri': chosen_album["uri"],
            'images': chosen_album["images"][0]["url"],
        }
        items = self.sp.album_tracks(album_details["id"])["items"]
        album_details['album_tracks'] = [
            {
                "name": item['name'],
                "uri":item['uri'],
                "artists":item["artists"][0]["name"]} for item in items]
        return album_details

    def get_top_10(self, top_10):
        top_tracks = [
            self.song(
                item["song"],
                item["title"],
                None) for item in top_10]
        top_songs = [{"name": track['name'], "uri":track['uri'],
                      "artist": track["artists"][0]} for track in top_tracks]
        return top_songs
