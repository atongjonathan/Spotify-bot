import spotipy
from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET
from logging_config import logger
from spotipy.oauth2 import SpotifyClientCredentials


class Spotify():
    SPOTIPY_CLIENT_ID = SPOTIPY_CLIENT_ID
    SPOTIPY_CLIENT_SECRET = SPOTIPY_CLIENT_SECRET
    SCOPE = "playlist-modify-private"
    TOKEN_CACHE_PATH = "token.txt"

    def __init__(self) -> None:
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID,
                                                                        client_secret=SPOTIPY_CLIENT_SECRET))

    def artist(self, name: str) -> dict:
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
        chosen_artist = None
        for artist in most_popular:
            if name in str(artist["name"]).lower():
                chosen_artist = artist
                break
        images_data = chosen_artist["images"]

        # return self.top_songs,self.top_tracks['tracks'][:no_of_tracks]
        artist_details = {
            'uri': chosen_artist["uri"],
            'followers': chosen_artist["followers"]["total"],
            'images': [item["url"] for item in images_data][0],
            'name': chosen_artist["name"],
            'genres': [genre.title() for genre in chosen_artist["genres"]],
        }
        top_tracks = self.sp.artist_top_tracks(artist_details["uri"])['tracks']
        artist_albums = self.sp.artist_albums(
            artist_details['uri'], album_type='album')
        artist_singles = self.sp.artist_albums(
            artist_details['uri'], album_type='single')
        artist_complilations = self.sp.artist_albums(
            artist_details['uri'], album_type='compilation')
        artist_details['album'] = [
            {"name": item['name'], "uri":item['uri']} for item in artist_albums['items']]
        artist_details['top_songs'] = [
            {"name": track['name'], "uri":track['uri']} for track in top_tracks]
        artist_details['single'] = [
            {"name": item['name'], "uri":item['uri']} for item in artist_singles['items']]
        artist_details['compilation'] = [
            {"name": item['name'], "uri":item['uri']} for item in artist_complilations['items']]
        return artist_details

    def song(self, artist, title, uri) -> dict:
        if uri is not None:
            chosen_song = self.sp.track(uri)
        else:
            """Get all possible details of an track"""
            track_data = self.sp.search(q=f"{artist} {title}", type="track")
            possible_tracks = track_data["tracks"]["items"]
            if len(possible_tracks) == 0:
                logger.info(f"No tracks found for {artist}, {title}")
                return
            chosen_song = possible_tracks[0]
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
