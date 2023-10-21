import telebot
import requests
import os
from io import BytesIO
import time
from telebot import util
from audio import Audio
from spotify import Spotify
from keyboards import Keyboard
from get_lyrics import lyrics_extractor_lyrics, musicxmatch_lyrics
from config import TELEGRAM_BOT_TOKEN
from logging_config import logger

bot = telebot.TeleBot((TELEGRAM_BOT_TOKEN), parse_mode='markdown')
base_url = "https://open.spotify.com/track/"
MAX_RETRIES = 5
keyboards_list = []

spotify = Spotify()
keyboard = Keyboard()
audio = Audio()


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
        "Awesome, send the name of the song with the artist separated by a comma",
        reply_markup=keyboard.force_markup)
    bot.register_next_step_handler_by_chat_id(
        message.chat.id, lambda message: send_song_data(message))


@bot.message_handler(commands=['commands'])
def info(message):
    bot.reply_to(
        message,
        "/start - Starts the bot\n/song - Search for a song\n/artist - Search for an artist\n/ping - Test Me")
# /topsongs - Get top 10 tracks in the world")


@bot.message_handler(commands=['log'])
def get_logs(message):
    with open('logs.txt') as file:
        bot.send_document(
            message.chat.id,
            file,
            reply_markup=keyboard.start_markup)


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
    artist_details = spotify.artist(message.text)
    if artist_details is None:
        bot.send_message(
            message.chat.id,
            f"Artist `{message.text}` not found!⚠. Please check your spelling and also include special characters.\nTry again? /artist",
            reply_markup=keyboard.start_markup)
        return
    caption = f'👤Artist: `{artist_details["name"]}`\n🧑Followers: `{artist_details["followers"]:,}` \n🎭Genre(s): `{", ".join(artist_details["genres"])}` \n'
    lists_of_type = [artist_details["artist_singles"]["single"], artist_details["artist_albums"]["album"],artist_details["artist_compilations"]["compilation"]]
    lengths = [len(item) for item in lists_of_type]
    pin = bot.send_photo(
        message.chat.id,
        photo=artist_details["images"],
        caption=caption,
        reply_markup=keyboard.view_handler(
            artist_details["name"], lengths))
    bot.pin_chat_message(message.chat.id, pin.id)


@retry_func
def send_song_data(message):
    artist, title = check_input(message)
    track_details = spotify.song(artist, title, None)
    caption = f'👤Artist: `{", ".join(track_details["artists"])}`\n🎵Song : `{track_details["name"]}`\n━━━━━━━━━━━━\n📀Album : `{track_details["album"]}`\n🔢Track : {track_details["track_no"]} of {track_details["total_tracks"]}\n⭐️ Released: `{track_details["release_date"]}`'
    send_audios_or_previews(track_details, caption, message.chat.id, True)


def send_audios_or_previews(track_details, caption, chat_id, send_photo):
    track_url = track_details['external_url']
    reply_markup = keyboard.lyrics_handler(
            track_details['name'], track_details['uri'])
    if send_photo:
        time.sleep(1)
        bot.send_photo(
            chat_id,
            photo=track_details['image'],
            caption=caption,
            reply_markup=keyboard.start_markup)
    update = bot.send_message(chat_id, "... Downloading song just a sec ...")
    data = None
    # query = f"{name} {artist}"
    # data = audio.download_webm(f"{query}", name)
    bot.edit_message_text(
        "Adding metadata😇...",
        chat_id=chat_id,
        message_id=update.message_id)
    if data is not None:
        files = [f for f in os.listdir(
            '.') if os.path.isfile(f) and f.endswith('.mp3')]
        audio.set_metadata(artist, track_details["release_date"], track_details["album"],
                           track_details["name"], track_details["track_no"], track_details["images"], files[0])
        path = files[0]
        with open(path, "rb") as file:
            bot.send_chat_action(chat_id, "upload_audio")
            bot.send_audio(chat_id, audio=file, title=f'{track_details["name"]}', performer=track_details["artists"],
                           reply_markup=reply_markup, caption="@JonaAtong")
        os.remove(path)
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
        track_details = spotify.song("", "", uri)
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
            track_details = spotify.song("", "", id)
            caption = f'👤Artist: `{artist}`\n🔢Track : {track_details["track_no"]} of {album_details["total_tracks"]}\n🎵Song : `{track_details["name"]}`\n'
            send_audios_or_previews(track_details, caption, chat_id, False)
        bot.send_message(
            chat_id, f'Those are all the {track_details["total_tracks"]} track(s) in "`{album_details["name"]}`" by `{artist}`. 💪!', reply_markup=keyboard.start_markup)


def send_checker(list_of_type, chat_id, current_page=0):
    reply_markup=keyboard.make_for_type(list_of_type, current_page)
    try:
        board = keyboards_list[0]["keyboard"]
        bot.edit_message_reply_markup(chat_id,board.message_id,reply_markup=reply_markup)
    except:
        make = bot.send_message(
            chat_id,
            "Awesome which ones tracks do you want to get?",reply_markup=reply_markup
            )
        make_dict = {"name": 'make', "keyboard": make}
        keyboards_list.append(make_dict)


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


def process_callback_query(call):
    try:
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
        else:
            uri = call.data
            get_album_songs(uri, call.message.chat.id)
    except Exception as e:
        logger.error(f"Error processing callback query: {str(e)}")
        bot.send_message(
            call.message.chat.id,
            "`An error occurred while processing your request. Please try again later.`")


def handle_list_callback(call):
    type = call.data.split("_")[0]
    artist = call.data.split("_")[1]
    artist_details = spotify.artist(artist)
    if type == "toptracks":
        artist_list = artist_details["top_songs"]
    else:
        artist_list = artist_details[f"artist_{type}s"]
    send_checker(artist_list, call.message.chat.id)


def handle_top_tracks_callback(call):
    send_top_songs(call)

def handle_pagination_callback(call):
    handle = call.data.split('_')[1]
    artist = call.data.split('_')[2]
    type = call.data.split('_')[3]
    page = call.data.split('_')[4]
    artist_details = spotify.artist(artist)
    if type is None or "artist_Nones":
        list_of_type = artist_details[f"top_songs"]
    else:
        list_of_type = artist_details[f"artist_{type}s"]    
    if handle == 'n':
        page = int(page)+1
        send_checker(list_of_type,call.message.chat.id, page)
    if handle == 'p':
        page = int(page)-1
        send_checker(list_of_type,call.message.chat.id, page)


def handle_lyrics_callback(call):
    uri = call.data.split("_")[1]
    track_details = spotify.song("", "", uri)
    artist = ', '.join(track_details['artists'])
    title = track_details["name"]
    try:
        lyrics = lyrics_extractor_lyrics(artist,title)
        logger.info("Lyrics by Lyrics Extractor")
    except:
        lyrics = musicxmatch_lyrics(artist,title)
        logger.info("Lyrics by MusixMatch")
    caption = f"👤Artist: `{', '.join(track_details['artists'])}`\n🎵Song : `{track_details['name']}`\n━━━━━━━━━━━━\n📀Album : `{track_details['album']}`\n🔢Track : {track_details['track_no']} of {track_details['total_tracks']}\n⭐️ Released: `{track_details['release_date']}`\n\n🎶Lyrics📝:\n\n`{lyrics}`"
    try:
        bot.send_message(
            call.message.chat.id,
            text=caption,
            reply_markup=keyboard.start_markup)
    except BaseException:
        splitted_text = util.smart_split(
            caption,
            chars_per_string=3000,
            reply_markup=keyboard.start_markup)
        for text in splitted_text:
            bot.send_message(
                call.message.chat.id,
                text=text,
                reply_markup=keyboard.start_markup)


def handle_close_callback(call):
    off = call.data.split("_")[1]
    if off == "make":
        for board in keyboards_list:
            if board["name"] == 'make':
                keyboards_list.remove(board)
                bot.delete_message(call.message.chat.id, board["keyboard"].id)
            if board["name"] == 'handler':
                bot.delete_message(call.message.chat.id, board["keyboard"].id)


# Set up a callback query handler
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    process_callback_query(call)


if __name__ == '__main__':
    logger.info("Bot is running :>")
    bot.polling()
