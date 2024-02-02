import os
from spotify import Spotify
from keyboards import Keyboard
from logging import getLogger
import billboard
from get_lyrics import musicxmatch_lyrics
from logging import getLogger
import time
import requests
from io import BytesIO
from telebot import util
from functions import download
from config import TELEGRAM_BOT_TOKEN
import telebot


class SGBot():
    def __init__(self) -> None:
        self.BOT = telebot.TeleBot((TELEGRAM_BOT_TOKEN), parse_mode='markdown')
        self.isPreview = False
        self.keyboards_list = []
        self.spotify = Spotify()
        self.keyboard = Keyboard()
        self.logger = getLogger(__name__)
        self.make_id = None

    def reply_to_query(self, message, reply_text, search_function):
        self.BOT.reply_to(message, reply_text,
                          reply_markup=self.keyboard.force_markup)
        self.BOT.register_next_step_handler_by_chat_id(message.chat.id,
                                                       lambda msg: search_function(msg))

    def get_search_query(self, message, command, function, reply_text):
        text = message.text
        if " " in text:
            query = text.replace(f"/{command} ", "")
            function(message, query)
        else:
            self.reply_to_query(message, reply_text, function)

    def search_trending(self, message, no_of_songs):
        reply = self.BOT.send_message(
            message.chat.id, "Awesome getting trending somgs in a few")
        hot_100 = billboard.ChartData("hot-100")[:no_of_songs]
        track_details = [self.spotify.song(artist=item.artist, title=item.title)[
            0] for item in hot_100]
        result_string = [
            f'{idx+1}. `{item["name"]}` - {item["artists"]}' for idx, item in enumerate(track_details)]
        result_string = '\n'.join(result_string)
        artists_keyboard = self.keyboard.keyboard_for_results(
            results=track_details)
        self.BOT.delete_message(reply.chat.id, reply.id)
        self.BOT.send_message(
            message.chat.id,
            f"Trending Songs\n\n{result_string}",
            reply_markup=artists_keyboard)

    def send_top_songs(self, call):
        name = call.data.split('_')[1]
        artist_details = self.spotify.artist(name)
        top_tracks = artist_details["top_songs"]
        caption = f'👤Artist: {artist_details["name"]}\n🧑Followers: {artist_details["followers"]:,} \n🎭Genre(s): {", ".join(artist_details["genres"])} \n⏬Top Tracks⏬'
        self.BOT.send_photo(call.message.chat.id,
                            photo=artist_details["images"],
                            caption=caption,
                            reply_markup=self.keyboard.start_markup)
        for track in top_tracks:
            track_details = self.spotify.song(
                artist_details["name"], track, None)
            try:
                caption = f'👤Artist: `{", ".join(track_details["artists"])}`\n🔢Track : {track_details["track_no"]} of {track_details["total_tracks"]}\n🎵Song : `{track_details["name"]}`\n'
            except BaseException:
                continue
            self.send_audios_or_previews(track_details, caption,
                                         call.message.chat.id, True)
        self.BOT.send_message(
            call.message.chat.id,
            f'Those are `{artist_details["name"]}`\'s top 🔝 10 tracks 💪!',
            reply_markup=self.keyboard.start_markup)
        return

    def search_song(self, message, query=None):
        """
        Search for the song from the string provided.

        Args:
            message: Telegram message object

        Returns:
            None
        """
        if query != None:
            artist, title = self.check_input(query)
        else:
            query = message.text
            artist, title = self.check_input(query)
        possible_tracks = self.spotify.song(artist, title)
        no_of_results = len(possible_tracks)
        if no_of_results == 0:
            self.BOT.send_message(
                message.chat.id,
                f"`{title}` not found!⚠. Please check your spelling and also include special characters.\nTry again?",
                reply_markup=self.keyboard.start_markup)
            return
        result_string = [
            f"{idx+1}. `{item['name']}` - {item['artists']}"
            for idx, item in enumerate(possible_tracks)
        ]
        result_string = '\n'.join(result_string)
        artists_keyboard = self.keyboard.keyboard_for_results(
            results=possible_tracks)
        self.BOT.send_message(
            message.chat.id,
            f"Found {no_of_results} result(s) from the search `{title}` ~ {message.from_user.first_name}\n\n{result_string}",
            reply_markup=artists_keyboard)

    def search_artist(self, message, artist=None) -> None:
        """
        Search for the artist from the string provided.

        Args:
            message: Telegram message object

        Returns:
            None
        """
        if artist != None:
            artist_results = self.spotify.artist(
                artist)
        else:
            artist = message.text
            # Search for list of possible artists
            artist_results = self.spotify.artist(artist)
        if artist_results is None:  # Handles when no artist is found
            self.BOT.send_message(
                message.chat.id,
                f"Artist `{message.text}` not found!⚠. Please check your spelling and also include special characters.\nTry again.",
                reply_markup=self.keyboard.start_markup)
            return
        # When artists are found
        no_of_results = len(artist_results)
        result_string = [
            f"{idx+1}. `{item['name']}` ~ Followers: {item['followers']}"
            for idx, item in enumerate(artist_results)
        ]
        # Text to send the user to see the results
        result_string = '\n'.join(result_string)
        # Make keyboard for corresponding possible artists
        artists_keyboard = self.keyboard.keyboard_for_results(
            results=artist_results)
        self.BOT.send_message(
            message.chat.id,
            f"Found {no_of_results} result(s) from the search `{artist}` ~ {message.from_user.first_name}\n\n{result_string}",
            reply_markup=artists_keyboard)

    def send_chosen_artist(self, artist_details, message):
        """
        Sends back the requested artist details with a reply markup for specificity of which type
        """
        caption = f'👤Artist: `{artist_details["name"]}`\n🧑Followers: `{artist_details["followers"]:,}` \n🎭Genre(s): `{", ".join(artist_details["genres"])}` \n'
        lists_of_type = [
            artist_details["artist_singles"]["single"],
            artist_details["artist_albums"]["album"],
            artist_details["artist_compilations"]["compilation"]
        ]
        # Get lengths to check if these lists requested exist for the artist
        lengths = [len(item) for item in lists_of_type]
        pin = self.BOT.send_photo(message.chat.id,
                                  photo=artist_details["images"],
                                  caption=caption,
                                  reply_markup=self.keyboard.view_handler(
                                      artist_details["name"], artist_details["uri"],
                                      lengths))
        self.BOT.pin_chat_message(message.chat.id, pin.id)

    def send_audios_or_previews(self, track_details, caption, chat_id, send_photo):
        track_url = track_details['external_url']
        reply_markup = self.keyboard.lyrics_handler(track_details['name'],
                                                    track_details['uri'])
        title = track_details["name"]
        if send_photo:
            time.sleep(1)
            keyboard = self.keyboard.link_handler(track_url)
            self.BOT.send_photo(chat_id,
                                photo=track_details['image'],
                                caption=caption,
                                reply_markup=keyboard)
        update = self.BOT.send_message(
            chat_id, f"...⚡Downloading track no {track_details['track_no']} - `{title}`⚡ ...")
        if self.isPreview:
            if track_details['preview_url'] is None:
                keyboard = self.keyboard.link_handler(track_url)
                self.BOT.send_message(chat_id,
                                      text=f"No Preview found for `{title}`",
                                      reply_markup=keyboard)
            else:
                response = requests.get(track_details['preview_url'])
                audio_content = response.content
                audio_io = BytesIO(audio_content)
                self.BOT.send_chat_action(chat_id, "upload_audio")
                self.BOT.send_audio(chat_id, audio_io, title=title,
                                    performer=track_details['artists'][0],
                                    reply_markup=reply_markup,
                                    caption=f"#{''.join(track_details['artists']).replace(' ', '')}")

        else:
            if (download(track_link=track_url)):
                for f in os.listdir('output'):
                    file_path = os.path.join("output", f)
                    if file_path.endswith(".mp3"):
                        with open(file_path, "rb") as file:
                            self.logger.info(f"Sending {f}", )
                            self.BOT.send_chat_action(chat_id, "upload_audio")
                            song = self.BOT.send_audio(chat_id, file, title=title,
                                                       performer=track_details['artists'][0],
                                                       reply_markup=reply_markup,
                                                       caption=f"#{''.join(track_details['artists']).replace(' ', '')}")
                        self.logger.info("Sent successfully")
                        os.remove(file_path)
        self.BOT.delete_message(chat_id, update.message_id)

    def get_album_songs(self, uri, chat_id):
        album_details = self.spotify.album("", "", uri)
        if isinstance(album_details, str):
            track_details = self.spotify.get_chosen_song(uri)
            self.send_chosen_track(track_details, chat_id)
        else:
            caption = f'👤Artist: `{", ".join(album_details["artists"])}`\n📀 Album: `{album_details["name"]}`\n⭐️ Released: `{album_details["release_date"]}`\n🔢 Total Tracks: {album_details["total_tracks"]}'
            self.BOT.send_photo(chat_id,
                                album_details["images"],
                                caption=caption,
                                reply_markup=self.keyboard.start_markup)
            album_tracks = album_details['album_tracks']
            for track in album_tracks:
                id = track["uri"]
                track_details = self.spotify.get_chosen_song(id)
                caption = f'👤Artist: `{track_details["artists"]}`\n🔢Track : {track_details["track_no"]} of {album_details["total_tracks"]}\n🎵Song : `{track_details["name"]}`\n'
                self.send_audios_or_previews(
                    track_details, caption, chat_id, False)
            self.BOT.send_message(
                chat_id,
                f'Those are all the {track_details["total_tracks"]} track(s) in "`{album_details["name"]}`" by `{", ".join(album_details["artists"])}`. 💪!',
                reply_markup=self.keyboard.start_markup)

    def send_checker(self, list_of_type: list, chat_id: str, current_page: int):
        """
        Requests user to specify the song to get with appropriate reply markup
        """
        try:
            reply_markup = self.keyboard.make_for_type(
                list_of_type, current_page)
        except BaseException:
            reply_markup = self.keyboard.make_for_trending(list_of_type)
        try:
            self.BOT.edit_message_reply_markup(
                chat_id, self.make_id, reply_markup=reply_markup)
        except Exception as e:
            make = self.BOT.send_message(chat_id,
                                         "Awesome which ones tracks do you want to get?",
                                         reply_markup=reply_markup)
            self.make_id = make.id

    def check_input(self, query):
        if "," not in query:
            query + ","
        data_list = query.split(",")
        title = data_list[0]
        try:
            artist = data_list[1]
        except BaseException:
            artist = ""
        return artist, title

    def process_callback_query(self, call):
        data = call.data
        if data.startswith('album') or data.startswith('single') or data.startswith(
            'compilation') or data.startswith(
                'toptracks'):  # Handle for list of type of an artist
            self.BOT.answer_callback_query(call.id)
            self.handle_list_callback(call)
        elif data.startswith("lyrics"):  # Handle for sending lyrics of a song
            self.handle_lyrics_callback(call)
        elif data.startswith("close"):
            # Handle for closing all Inline markups
            self.BOT.answer_callback_query(call.id)
            self.handle_close_callback(call)
        elif data.startswith("_"):
            self.BOT.answer_callback_query(call.id)
            self.handle_pagination_callback(call)
        elif data.startswith("result_"):  # Handle for possible results of an artist
            self.BOT.answer_callback_query(call.id)
            self.handle_result_callback(call)
        else:
            self.BOT.delete_message(call.message.chat.id, call.message.id)
            self.get_album_songs(data, call.message.chat.id)

    def handle_list_callback(self, call):
        """
        Uses type, and uri to get list of type or top_tracks and calls send_checker using that info
        """
        type = call.data.split("_")[0]
        uri = call.data.split("_")[1]
        artist_details = self.spotify.get_chosen_artist(uri)
        if type == "toptracks":
            # A LIST of dictionary tracks with name, uri and artist_uri
            artist_list = artist_details["top_songs"]
        else:
            artist_list = artist_details[f"artist_{type}s"]
        self.send_checker(artist_list, call.message.chat.id, 0)

    def handle_top_tracks_callback(self, call):
        self.send_top_songs(call)

    def handle_result_callback(self, call):
        """
        Calls either the track or artist method to reply to the user with requested info
        """
        self.BOT.delete_message(
            call.message.chat.id,
            call.message.id)  # Deletes user manual for possible artists
        # Obtains the uri whether artist or track
        uri = call.data.split("_")[1]
        try:
            # Use the wrong uri type error to distinguish between artist or track
            # Use the uri to search for all possible artist data
            artist_details = self.spotify.get_chosen_artist(uri)
            self.send_chosen_artist(artist_details, call.message)
        except BaseException:
            track_details = self.spotify.get_chosen_song(uri)
            self.send_chosen_track(track_details, call.message.chat.id)

    def handle_pagination_callback(self, call):
        handle = call.data.split('_')[1]
        artist = call.data.split('_')[2]
        of_type = call.data.split('_')[3]
        page = call.data.split('_')[4]
        artist_details = self.spotify.get_chosen_artist(artist)
        if of_type == "toptracks":
            artist_list = artist_details["top_songs"]
        else:
            artist_list = artist_details[f"artist_{of_type}s"]
        if handle == 'n':
            page = int(page) + 1
            self.send_checker(artist_list, call.message.chat.id, page)
        elif handle == 'p':
            page = int(page) - 1
            self.send_checker(artist_list, call.message.chat.id, page)

    def handle_lyrics_callback(self, call):
        uri = call.data.split("_")[1]
        track_details = self.spotify.get_chosen_song(uri)
        artist = ', '.join(track_details['artists'])
        title = track_details["name"]
        try:
            lyrics = musicxmatch_lyrics(artist, title)
        except Exception as e:
            self.logger.error(e)
            lyrics = None
        if lyrics == None or lyrics == "":
            self.BOT.answer_callback_query(
                call.id, text=f"'{title}' lyrics not found!", show_alert=True)
        else:
            self.BOT.answer_callback_query(call.id)
            caption = f"👤Artist: `{', '.join(track_details['artists'])}`\n🎵Song : `{track_details['name']}`\n━━━━━━━━━━━━\n📀Album : `{track_details['album']}`\n🔢Track : {track_details['track_no']} of {track_details['total_tracks']}\n⭐️ Released: `{track_details['release_date']}`\n\n🎶Lyrics📝:\n\n`{lyrics}`"
            try:
                self.BOT.reply_to(call.message,
                                  text=caption,
                                  reply_markup=self.keyboard.start_markup)
            except BaseException:
                splitted_text = util.smart_split(
                    caption, chars_per_string=3000)
                for text in splitted_text:
                    try:
                        self.BOT.reply_to(call.message,
                                          text=caption,
                                          reply_markup=self.keyboard.start_markup)
                    except Exception as e:
                        self.BOT.answer_callback_query(call.id, e)

    def handle_close_callback(self, call):
        self.BOT.delete_message(call.message.chat.id, call.message.id)

    def send_chosen_track(self, track_details, chat_id):
        duration = track_details["duration_ms"]
        minutes = duration // 60000
        seconds = int((duration % 60000)/1000)
        caption = f'👤Artist: `{", ".join(track_details["artists"])}`\n🎵Song : `{track_details["name"]}`\n━━━━━━━━━━━━\n📀Album : `{track_details["album"]}`\n🔢Track : {track_details["track_no"]} of {track_details["total_tracks"]}\n⭐️ Released: `{track_details["release_date"]}`\n⌚Duration: `{minutes}:{seconds}`\n🔞Is Explicit: {track_details["explicit"]}\n'
        self.send_audios_or_previews(track_details, caption, chat_id, True)
