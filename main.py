import telebot
import requests
import os
from io import BytesIO
import time
from telebot import util, types
from spotify import Spotify
from keyboards import Keyboard
from get_lyrics import azlyrics, lyrics_extractor_lyrics, musicxmatch_lyrics, lyricsgenius_lyrics
from config import TELEGRAM_BOT_TOKEN
from billboard import get_billboard_hot_100
import json
import warnings
from logging import FileHandler, StreamHandler, INFO, basicConfig, getLogger

basicConfig(format='%(levelname)s | %(asctime)s - %(name)s - line %(lineno)d | %(message)s',
            handlers=[FileHandler('logs.txt'), StreamHandler()], level=INFO)
logger = getLogger(__name__)

# Filter out specific warnings from spotipy.cache_handler
warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    module="spotipy.cache_handler")


bot = telebot.TeleBot((TELEGRAM_BOT_TOKEN), parse_mode='markdown')
base_url = "https://open.spotify.com/track/"
MAX_RETRIES = 5
keyboards_list = []
spotify = Spotify()
keyboard = Keyboard()


def retry_func(func):
    def wrapper(*args, **kwargs):
        retries = 0
        while retries < MAX_RETRIES:
            try:
                return func(*args, **kwargs)
            except ConnectionError as e:
                logger.info(f"Error {retries},{e} \n Retrying...")
            except Exception as e:
                logger.error(
                    f"Trial {retries}: Another exception occurred, {e}")
            retries += 1
        logger.info("Max Retries reached")
        return None
    return wrapper


def send_top_songs(call):
    name = call.data.split('_')[1]
    artist_details = spotify.artist(name)
    top_tracks = artist_details["top_songs"]
    caption = f'👤Artist: {artist_details["name"]}\n🧑Followers: {artist_details["followers"]:,} \n🎭Genre(s): {", ".join(artist_details["genres"])} \n⏬Top Tracks⏬'
    bot.send_photo(
        call.message.chat.id,
        photo=artist_details["images"],
        caption=caption,
        reply_markup=keyboard.start_markup)
    for track in top_tracks:
        track_details = spotify.song(artist_details["name"], track, None)
        try:
            caption = f'👤Artist: `{", ".join(track_details["artists"])}`\n🔢Track : {track_details["track_no"]} of {track_details["total_tracks"]}\n🎵Song : `{track_details["name"]}`\n'
        except BaseException:
            continue
        send_audios_or_previews(
            track_details,
            caption,
            call.message.chat.id,
            True)
    bot.send_message(
        call.message.chat.id, f'Those are `{artist_details["name"]}`\'s top 🔝 10 tracks 💪!', reply_markup=keyboard.start_markup)
    return


def search_artist(message) -> None:
    artist_results = spotify.artist(message.text)
    no_of_results = len(artist_results)
    if no_of_results == 0:
        bot.send_message(
            message.chat.id,
            f"Artist `{message.text}` not found!⚠. Please check your spelling and also include special characters.\nTry again? /artist",
            reply_markup=keyboard.start_markup)
        return
    result_string = [
        f"{idx+1}. `{item['name']}` ~ Followers: {item['followers']}" for idx,
        item in enumerate(artist_results)]
    result_string = '\n'.join(result_string)
    artists_keyboard = keyboard.keyboard_for_results(results=artist_results)
    bot.send_message(
        message.chat.id,
        f"Found {no_of_results}result(s) from the search `{message.text}` ~ {message.from_user.first_name}\n\n{result_string}",
        reply_markup=artists_keyboard)


def send_chosen_artist(artist_details, message):
    caption = f'👤Artist: `{artist_details["name"]}`\n🧑Followers: `{artist_details["followers"]:,}` \n🎭Genre(s): `{", ".join(artist_details["genres"])}` \n'
    lists_of_type = [
        artist_details["artist_singles"]["single"],
        artist_details["artist_albums"]["album"],
        artist_details["artist_compilations"]["compilation"]]
    lengths = [len(item) for item in lists_of_type]
    pin = bot.send_photo(
        message.chat.id,
        photo=artist_details["images"],
        caption=caption,
        reply_markup=keyboard.view_handler(
            artist_details["name"], artist_details["uri"], lengths))
    bot.pin_chat_message(message.chat.id, pin.id)


def send_audios_or_previews(track_details, caption, chat_id, send_photo):
    track_url = track_details['external_url']
    reply_markup = keyboard.lyrics_handler(
        track_details['name'], track_details['uri'])
    artist = ', '.join(track_details['artists'])
    title = track_details["name"]
    if send_photo:
        time.sleep(1)
        bot.send_photo(
            chat_id,
            photo=track_details['image'],
            caption=caption,
            reply_markup=keyboard.start_markup)
    update = bot.send_message(chat_id, "... Downloading song just a sec ...")
    query = f"{title} {artist}"
    data = None
    if data is not None:
        # bot.edit_message_text(
        # "Adding metadata😇...",
        # chat_id=chat_id,
        # message_id=update.message_id)
        for f in os.listdir('.'):
            if os.path.isfile(f) and f.endswith('.webm'):
                old_name = f.split(".webm")[0]
                new_name = f.replace('.webm', '.mp3').replace(old_name, title)
                print(old_name, "\n", new_name)
                os.rename(f, new_name)

        # audio.set_metadata(track_details, new_name)
        with open(new_name, "rb") as file:
            bot.send_chat_action(chat_id, "upload_audio")
            bot.send_audio(chat_id, audio=file, title=f'{track_details["name"]}', performer=track_details["artists"],
                           reply_markup=reply_markup, caption="@JonaAtong")
        os.remove(new_name)
    elif track_details['preview_url'] is None:
        bot.send_message(
            chat_id,
            text=f"{track_url}",
            reply_markup=keyboard.start_markup)
    else:
        response = requests.get(track_details['preview_url'])
        audio_content = response.content
        audio_io = BytesIO(audio_content)
        bot.send_chat_action(chat_id, "upload_audio")
        bot.send_audio(chat_id, audio=audio_io,
                       title=f"{track_details['name']}", performer=track_details['artists'], reply_markup=reply_markup, caption="@JonaAtong")
    bot.delete_message(chat_id, update.id)


def get_album_songs(uri, chat_id):
    album_details = spotify.album("", "", uri)
    if isinstance(album_details, str):
        track_details = spotify.get_chosen_song(uri)
        caption = f'👤Artist: `{ ", ".join(track_details["artists"])}`\n🔢Track : {track_details["track_no"]} of {track_details["total_tracks"]}\n🎵Song : `{track_details["name"]}`\n'
        send_audios_or_previews(track_details, caption, chat_id, True)
    else:
        caption = f'👤Artist: `{", ".join(album_details["artists"])}`\n📀 Album: `{album_details["name"]}`\n⭐️ Released: `{album_details["release_date"]}`\n🔢 Total Tracks: {album_details["total_tracks"]}'
        bot.send_photo(
            chat_id,
            album_details["images"],
            caption=caption,
            reply_markup=keyboard.start_markup)
        album_tracks = album_details['album_tracks']
        for track in album_tracks:
            id = track["uri"]
            artist = track["artists"]
            track_details = spotify.get_chosen_song(id)
            caption = f'👤Artist: `{artist}`\n🔢Track : {track_details["track_no"]} of {album_details["total_tracks"]}\n🎵Song : `{track_details["name"]}`\n'
            send_audios_or_previews(track_details, caption, chat_id, False)
        bot.send_message(
            chat_id, f'Those are all the {track_details["total_tracks"]} track(s) in "`{album_details["name"]}`" by `{artist}`. 💪!', reply_markup=keyboard.start_markup)


def send_checker(list_of_type, chat_id, current_page):
    reply_markup = keyboard.make_for_type(list_of_type, current_page)
    global make_id
    try:
        bot.edit_message_reply_markup(
            chat_id, make_id, reply_markup=reply_markup)
    except Exception:
        make = bot.send_message(
            chat_id,
            "Awesome which ones tracks do you want to get?", reply_markup=reply_markup
        )
        make_id = make.id


def check_input(message):
    text_message = message.text
    if "," not in message.text:
        text_message = message.text + ","
    data_list = text_message.split(",")
    title = data_list[0]
    try:
        artist = data_list[1]
    except BaseException:
        artist = ""
    return artist, title


def process_callback_query(call):
    data = call.data
    if data.startswith('album') or data.startswith('single') or data.startswith(
            'compilation') or data.startswith('toptracks'):
        handle_list_callback(call)
    elif data.startswith("toptracks"):
        handle_top_tracks_callback(call)
    elif data.startswith("lyrics"):
        handle_lyrics_callback(call)
    elif data.startswith("close"):
        handle_close_callback(call)
    elif data.startswith("_"):
        handle_pagination_callback(call)
    elif data.startswith("r_"):
        handle_result_callback(call)
    else:
        get_album_songs(data, call.message.chat.id)


def handle_list_callback(call):
    type = call.data.split("_")[0]
    uri = call.data.split("_")[1]
    artist_details = spotify.get_chosen_artist(uri)
    if type == "toptracks":
        artist_list = artist_details["top_songs"]
    else:
        artist_list = artist_details[f"artist_{type}s"]
    send_checker(artist_list, call.message.chat.id, 0)


def handle_top_tracks_callback(call):
    send_top_songs(call)


def handle_result_callback(call):
    bot.delete_message(call.message.chat.id, call.message.id)
    uri = call.data.split("_")[1]
    try:
        artist_details = spotify.get_chosen_artist(uri)
        send_chosen_artist(artist_details, call.message)
    except BaseException:
        track_details = spotify.get_chosen_song(uri)
        send_chosen_track(track_details, call.message)


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
    caption = f"👤Artist: `{', '.join(track_details['artists'])}`\n🎵Song : `{track_details['name']}`\n━━━━━━━━━━━━\n📀Album : `{track_details['album']}`\n🔢Track : {track_details['track_no']} of {track_details['total_tracks']}\n⭐️ Released: `{track_details['release_date']}`\n\n🎶Lyrics📝:\n\n`{lyrics}`"
    try:
        bot.send_message(
            call.message.chat.id,
            text=caption,
            reply_markup=keyboard.start_markup)
    except BaseException:
        splitted_text = util.smart_split(
            caption,
            chars_per_string=3000)
        for text in splitted_text:
            try:
                bot.send_message(
                    call.message.chat.id,
                    text=text,
                    reply_markup=keyboard.start_markup)
            except Exception as e:
                bot.answer_callback_query(call.id, e)


def handle_close_callback(call):
    bot.delete_message(call.message.chat.id, call.message.id)


def send_chosen_track(track_details, message):
    caption = f'👤Artist: `{", ".join(track_details["artists"])}`\n🎵Song : `{track_details["name"]}`\n━━━━━━━━━━━━\n📀Album : `{track_details["album"]}`\n🔢Track : {track_details["track_no"]} of {track_details["total_tracks"]}\n⭐️ Released: `{track_details["release_date"]}`'
    send_audios_or_previews(track_details, caption, message.chat.id, True)


@retry_func
def send_song_data(message):
    artist, title = check_input(message)
    possible_tracks = spotify.song(artist, title)
    no_of_results = len(possible_tracks)
    if no_of_results == 0:
        bot.send_message(
            message.chat.id,
            f"Song `{message.text}` not found!⚠. Please check your spelling and also include special characters.\nTry again? /song",
            reply_markup=keyboard.start_markup)
        return
    result_string = [
        f"{idx+1}. `{item['name']}` - {item['artists']}" for idx,
        item in enumerate(possible_tracks)]
    result_string = '\n'.join(result_string)
    artists_keyboard = keyboard.keyboard_for_results(results=possible_tracks)
    bot.send_message(
        message.chat.id,
        f"Found {no_of_results} result(s) from the search `{message.text}` ~ {message.from_user.first_name}\n\n{result_string}",
        reply_markup=artists_keyboard)


@bot.message_handler(commands=['start'])
def welcome(message):
    logger.info(
        f"{message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username} accessed Chat: {message.chat.id}")

    bot.send_message(
        message.chat.id,
        f"Hello `{message.from_user.first_name}`, Welcome to Spotify SG✨'s bot!. For help see commands?👉 /commands",
        reply_markup=keyboard.start_markup)


@bot.message_handler(commands=["artist"])
def artist(message):
    bot.send_message(
        message.chat.id,
        "Send me the name of the artist",
        reply_markup=keyboard.force_markup)
    bot.register_next_step_handler_by_chat_id(
        message.chat.id, lambda msg: search_artist(msg))


@bot.message_handler(commands=["song"])
def get_song(message):
    bot.send_message(
        message.chat.id,
        "Awesome, send the name of the song with the artist separated by a comma for optimal results",
        reply_markup=keyboard.force_markup)
    bot.register_next_step_handler_by_chat_id(
        message.chat.id, lambda message: send_song_data(message))


@bot.message_handler(commands=["top_songs"])
def top_songs(message):
    top_100 = get_billboard_hot_100()
    # top_10 = top_100[:9]
    long = ""
    for index, item in enumerate(top_100):
        long = f"{long}\n`{index+2}. {item['song']}-{item['title']}`\n"
    # list_of_type = (spotify.get_top_10(top_10))
    # send_checker(list_of_type, message.chat.id)
    edit = bot.send_message(message.chat.id, "Searching ... ⏳")
    bot.send_message(message.chat.id, long)
    bot.delete_message(message.chat.id, edit.message_id)


@bot.message_handler(commands=['commands'])
def info(message):
    bot.reply_to(
        message,
        "/start - Starts the bot\n/song - Search for a song\n/artist - Search for an artist\n/ping - Test Me")
# /topsongs - Get top 10 tracks in the world")


@bot.message_handler(commands=['logs'])
def get_logs(message):

    file = open("logs.txt")
    bot.send_document(
        message.chat.id,
        file,
        reply_markup=keyboard.start_markup)
    file.close()


@bot.message_handler(commands=['ping'])
def ping(message):
    start_time = time.time()
    response = bot.send_message(message.chat.id, "Pinging...")
    end_time = time.time()
    elapsed_time_ms = int((end_time - start_time) * 1000)

    bot.edit_message_text(
        f"Pong! 🏓\nResponse Time: `{elapsed_time_ms} ms`",
        chat_id=message.chat.id,
        message_id=response.message_id)


@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text == "⬆️ Show command buttons":
        bot.send_message(
            message.chat.id,
            "⬆️ Show command buttons",
            reply_markup=keyboard.start_markup)
    elif message.text == "⬇️ Hide command buttons":
        bot.send_message(
            message.chat.id,
            "⬇️ Hide command buttons",
            reply_markup=keyboard.hide_keyboard)


# Set up a callback query handler
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    bot.answer_callback_query(call.id)
    process_callback_query(call)


if __name__ == '__main__':
    logger.info("Bot is running :>")
    bot.polling()
