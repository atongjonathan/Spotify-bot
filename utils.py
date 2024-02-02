from spotify import Spotify
from keyboards import Keyboard
import telebot
from config import TELEGRAM_BOT_TOKEN
import os
import time
from get_lyrics import azlyrics, lyrics_extractor_lyrics, musicxmatch_lyrics, lyricsgenius_lyrics
from telebot import util
from logging import getLogger
from functions import download
import requests
from io import BytesIO


bot = telebot.TeleBot((TELEGRAM_BOT_TOKEN), parse_mode='markdown')
base_url = "https://open.spotify.com/track/"
MAX_RETRIES = 5
keyboards_list = []
spotify = Spotify()
keyboard = Keyboard()
logger = getLogger(__name__)


def send_top_songs(call):
    name = call.data.split('_')[1]
    artist_details = spotify.artist(name)
    top_tracks = artist_details["top_songs"]
    caption = f'👤Artist: {artist_details["name"]}\n🧑Followers: {artist_details["followers"]:,} \n🎭Genre(s): {", ".join(artist_details["genres"])} \n⏬Top Tracks⏬'
    bot.send_photo(call.message.chat.id,
                   photo=artist_details["images"],
                   caption=caption,
                   reply_markup=keyboard.start_markup)
    for track in top_tracks:
        track_details = spotify.song(artist_details["name"], track, None)
        try:
            caption = f'👤Artist: `{", ".join(track_details["artists"])}`\n🔢Track : {track_details["track_no"]} of {track_details["total_tracks"]}\n🎵Song : `{track_details["name"]}`\n'
        except BaseException:
            continue
        send_audios_or_previews(track_details, caption,
                                call.message.chat.id, True)
    bot.send_message(
        call.message.chat.id,
        f'Those are `{artist_details["name"]}`\'s top 🔝 10 tracks 💪!',
        reply_markup=keyboard.start_markup)
    return


def search_song(message, query=None):       
    """
      Search for the song from the string provided.

      Args:
        message: Telegram message object

      Returns:
        None
      """    
    if query != None:
        artist, title = check_input(query)
    else:
        query = message.text
        artist, title = check_input(query)
    possible_tracks = spotify.song(artist, title)
    no_of_results = len(possible_tracks)
    if no_of_results == 0:
        bot.send_message(
            message.chat.id,
            f"Song `{query}` not found!⚠. Please check your spelling and also include special characters.\nTry again? /song",
            reply_markup=keyboard.start_markup)
        return
    result_string = [
        f"{idx+1}. `{item['name']}` - {item['artists']}"
        for idx, item in enumerate(possible_tracks)
    ]
    result_string = '\n'.join(result_string)
    artists_keyboard = keyboard.keyboard_for_results(results=possible_tracks)
    bot.send_message(
        message.chat.id,
        f"Found {no_of_results} result(s) from the search `{query}` ~ {message.from_user.first_name}\n\n{result_string}",
        reply_markup=artists_keyboard)


def search_artist(message, artist=None) -> None:
    """
      Search for the artist from the string provided.

      Args:
        message: Telegram message object

      Returns:
        None
      """
    if artist != None:
        artist_results = spotify.artist(
            artist)
    else:
        artist = message.text
        # Search for list of possible artists
        artist_results = spotify.artist(artist)
    if artist_results is None:  # Handles when no artist is found
        bot.send_message(
            message.chat.id,
            f"Artist `{message.text}` not found!⚠. Please check your spelling and also include special characters.\nTry again? /artist",
            reply_markup=keyboard.start_markup)
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
    artists_keyboard = keyboard.keyboard_for_results(results=artist_results)
    bot.send_message(
        message.chat.id,
        f"Found {no_of_results} result(s) from the search `{artist}` ~ {message.from_user.first_name}\n\n{result_string}",
        reply_markup=artists_keyboard)


def send_chosen_artist(artist_details, message):
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
    pin = bot.send_photo(message.chat.id,
                         photo=artist_details["images"],
                         caption=caption,
                         reply_markup=keyboard.view_handler(
                             artist_details["name"], artist_details["uri"],
                             lengths))
    bot.pin_chat_message(message.chat.id, pin.id)


def send_audios_or_previews(track_details, caption, chat_id, send_photo):
    track_url = track_details['external_url']
    reply_markup = keyboard.lyrics_handler(track_details['name'],
                                           track_details['uri'])
    artist = ', '.join(track_details['artists'])
    title = track_details["name"]
    if send_photo:
        time.sleep(1)
        bot.send_photo(chat_id,
                       photo=track_details['image'],
                       caption=caption,
                       reply_markup=keyboard.start_markup)
    update = bot.send_message(chat_id, "...⚡Downloading song just a min⚡ ...")
    is_downloaded = download(track_url)
    if is_downloaded:
        for f in os.listdir('output'):
            file_path = os.path.join("output", f)
            if file_path.endswith(".mp3"):
                with open(file_path, "rb") as file:
                    logger.info(f"Sending {f}", )
                    bot.send_chat_action(chat_id, "upload_audio")
                    song = bot.send_audio(chat_id,
                                   file,
                                   title=title,
                                   performer=artist,
                                   reply_markup=reply_markup,
                                   caption=f"#{artist.replace(' ','')}")
                print(song.id, song.message_id)    
                logger.info("Sent successfully")
                os.remove(file_path)
            else:
                print(f, " is not a song")

    elif track_details['preview_url'] is None:
        bot.send_message(chat_id,
                         text=f"{track_url}",
                         reply_markup=keyboard.start_markup)
    else:
        response = requests.get(track_details['preview_url'])
        audio_content = response.content
        audio_io = BytesIO(audio_content)
        bot.send_chat_action(chat_id, "upload_audio")
        bot.send_audio(chat_id,
                       audio=audio_io,
                       title=f"{track_details['name']}",
                       performer=track_details['artists'],
                       reply_markup=reply_markup,
                       caption="@JonaAtong")
    bot.delete_message(chat_id, update.id)


def get_album_songs(uri, chat_id):
    album_details = spotify.album("", "", uri)
    if isinstance(album_details, str):
        track_details = spotify.get_chosen_song(uri)
        send_chosen_track(track_details, chat_id)
    else:
        caption = f'👤Artist: `{", ".join(album_details["artists"])}`\n📀 Album: `{album_details["name"]}`\n⭐️ Released: `{album_details["release_date"]}`\n🔢 Total Tracks: {album_details["total_tracks"]}'
        bot.send_photo(chat_id,
                       album_details["images"],
                       caption=caption,
                       reply_markup=keyboard.start_markup)
        album_tracks = album_details['album_tracks']
        for track in album_tracks:
            id = track["uri"]
            track_details = spotify.get_chosen_song(id)
            caption = f'👤Artist: `{track_details["artists"]}`\n🔢Track : {track_details["track_no"]} of {album_details["total_tracks"]}\n🎵Song : `{track_details["name"]}`\n'
            send_audios_or_previews(track_details, caption, chat_id, False)
        bot.send_message(
            chat_id,
            f'Those are all the {track_details["total_tracks"]} track(s) in "`{album_details["name"]}`" by `{album_details["artists"]}`. 💪!',
            reply_markup=keyboard.start_markup)


def send_checker(list_of_type: list, chat_id: str, current_page: int):
    """
      Requests user to specify the song to get with appropriate reply markup
      """
    try:
        reply_markup = keyboard.make_for_type(list_of_type, current_page)
    except BaseException:
        reply_markup = keyboard.make_for_trending(list_of_type)
    global make_id
    try:
        bot.edit_message_reply_markup(
            chat_id, make_id, reply_markup=reply_markup)
    except Exception as e:
        make = bot.send_message(chat_id,
                                "Awesome which ones tracks do you want to get?",
                                reply_markup=reply_markup)
        make_id = make.id


def check_input(query):
    if "," not in query:
        query + ","
    data_list = query.split(",")
    title = data_list[0]
    try:
        artist = data_list[1]
    except BaseException:
        artist = ""
    return artist, title


def process_callback_query(call):
    data = call.data
    if data.startswith('album') or data.startswith('single') or data.startswith(
        'compilation') or data.startswith(
            'toptracks'):  # Handle for list of type of an artist
        bot.answer_callback_query(call.id)
        handle_list_callback(call)
    elif data.startswith("lyrics"):  # Handle for sending lyrics of a song
        handle_lyrics_callback(call)
    elif data.startswith("close"):
        bot.answer_callback_query(call.id)  # Handle for closing all Inline markups
        handle_close_callback(call)
    elif data.startswith("_"):
        bot.answer_callback_query(call.id)
        handle_pagination_callback(call)
    elif data.startswith("result_"):  # Handle for possible results of an artist
        bot.answer_callback_query(call.id)
        handle_result_callback(call)
    else:
        bot.delete_message(call.message.chat.id, call.message.id)
        get_album_songs(data, call.message.chat.id)


def handle_list_callback(call):
    """
      Uses type, and uri to get list of type or top_tracks and calls send_checker using that info
      """
    type = call.data.split("_")[0]
    uri = call.data.split("_")[1]
    artist_details = spotify.get_chosen_artist(uri)
    if type == "toptracks":
        # A LIST of dictionary tracks with name, uri and artist_uri
        artist_list = artist_details["top_songs"]
    else:
        artist_list = artist_details[f"artist_{type}s"]
    send_checker(artist_list, call.message.chat.id, 0)


def handle_top_tracks_callback(call):
    send_top_songs(call)


def handle_result_callback(call):
    """
      Calls either the track or artist method to reply to the user with requested info
      """
    bot.delete_message(
        call.message.chat.id,
        call.message.id)  # Deletes user manual for possible artists
    uri = call.data.split("_")[1]  # Obtains the uri whether artist or track
    try:
        # Use the wrong uri type error to distinguish between artist or track
        # Use the uri to search for all possible artist data
        artist_details = spotify.get_chosen_artist(uri)
        send_chosen_artist(artist_details, call.message)
    except BaseException:
        track_details = spotify.get_chosen_song(uri)
        send_chosen_track(track_details, call.message.chat.id)


def handle_pagination_callback(call):
    handle = call.data.split('_')[1]
    artist = call.data.split('_')[2]
    of_type = call.data.split('_')[3]
    page = call.data.split('_')[4]
    artist_details = spotify.get_chosen_artist(artist)
    if of_type == "toptracks":
        artist_list = artist_details["top_songs"]
    else:
        artist_list = artist_details[f"artist_{of_type}s"]
    if handle == 'n':
        page = int(page) + 1
        send_checker(artist_list, call.message.chat.id, page)
    elif handle == 'p':
        page = int(page) - 1
        send_checker(artist_list, call.message.chat.id, page)


def handle_lyrics_callback(call):
    uri = call.data.split("_")[1]
    track_details = spotify.get_chosen_song(uri)
    artist = ', '.join(track_details['artists'])
    title = track_details["name"]
    try:
        logger.info("Searching by Lyrics Extractor")
        lyrics = lyrics_extractor_lyrics(artist, title)
    except BaseException:
        try:
            logger.info("Searching by Musicxmatch Extractor")
            lyrics = azlyrics(artist, title)
        except BaseException:
            try:
                logger.info("Searching by LyricsGenius Extractor")
                lyrics = lyricsgenius_lyrics(artist, title)
            except BaseException:
                lyrics = musicxmatch_lyrics(artist, title)
    if lyrics == None or lyrics == "":
        bot.answer_callback_query(call.id, text=f"'{title}' lyrics not found!",show_alert=True)
    else:
        bot.answer_callback_query(call.id)
        caption = f"👤Artist: `{', '.join(track_details['artists'])}`\n🎵Song : `{track_details['name']}`\n━━━━━━━━━━━━\n📀Album : `{track_details['album']}`\n🔢Track : {track_details['track_no']} of {track_details['total_tracks']}\n⭐️ Released: `{track_details['release_date']}`\n\n🎶Lyrics📝:\n\n`{lyrics}`"
        try:
            bot.reply_to(call.message,
                            text=caption,
                            reply_markup=keyboard.start_markup)
        except BaseException:
            splitted_text = util.smart_split(caption, chars_per_string=3000)
            for text in splitted_text:
                try:
                    bot.reply_to(call.message,
                                    text=caption,
                                    reply_markup=keyboard.start_markup)
                except Exception as e:
                    bot.answer_callback_query(call.id, e)


def handle_close_callback(call):
    bot.delete_message(call.message.chat.id, call.message.id)


def send_chosen_track(track_details, chat_id):
    duration = track_details["duration_ms"]
    minutes = duration // 60000
    seconds = int((duration % 60000)/1000)
    caption = f'👤Artist: `{", ".join(track_details["artists"])}`\n🎵Song : `{track_details["name"]}`\n━━━━━━━━━━━━\n📀Album : `{track_details["album"]}`\n🔢Track : {track_details["track_no"]} of {track_details["total_tracks"]}\n⭐️ Released: `{track_details["release_date"]}`\n⌚Duration: `{minutes}:{seconds}`\n🔞Explicit: {track_details["explicit"]}\n🚀Stream: {track_details["external_url"]}'
    send_audios_or_previews(track_details, caption, chat_id, True)



