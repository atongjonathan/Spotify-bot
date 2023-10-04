import telebot
import requests
import os
from io import BytesIO
import time
from telebot import util
from audio import Audio
from spotify import Spotify
from keyboards import Keyboard
from get_lyrics import extract_lyrics
from config import TELEGRAM_BOT_TOKEN
import logging
from speed import get_speed

bot = telebot.TeleBot((TELEGRAM_BOT_TOKEN))
base_url = "https://open.spotify.com/track/"
MAX_RETRIES = 5
keyboards_list = []
logger = logging.getLogger(__name__)


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
                logging.exception(f"Error {retries},{e} \n Retrying...")
            except Exception as e:
                logger.error(f"Another exception occurred, {e}")
            retries += 1
        logger.info("Max Retries reached")
        return None
    return wrapper

# Add a new chat and user to the dictionary


def add_chat_user(chat_id, fname, lname, uname):
    print(f"{fname} {lname} @{uname} accessed\nChat: {chat_id}")

@retry_func
def search_artist(message):
    if spotify.get_details_artist(message.text) is None:
        bot.send_message(message.chat.id,
                         "Artist not found!⚠. Make sure to include all artist name properties including supersripts.\nTry again? /artist")
        return
    artist_uri, followers, images, name, genres = spotify.get_details_artist(
        message.text)
    try:
        image = images[0]
    except IndexError:
        image = "https://cdn.business2community.com/wp-content/uploads/2014/03/Unknown-person.gif"
    genres = [item.title() for item in genres]
    list_of_albums = spotify.get_artist_albums(artist_uri, "album")
    list_of_singles = spotify.get_artist_albums(artist_uri, "single")
    album_names = []
    ep_names = []
    for index, dict in enumerate(list_of_singles):
        ep_names.append(str(index + 1) + '. ' + str(dict['name']) + "\n")
    for index, dict in enumerate(list_of_albums):
        album_names.append(str(index + 1) + '. ' + str(dict['name']) + "\n")

    caption = f"👤Artist: {name}\n🧑Followers: {followers:,} \n🎭Genre(s): {', '.join(genres)} \n"
    # full_board = keyboard.handler(name,artist_uri,list_of_albums,list_of_singles)
    pin = bot.send_photo(message.chat.id, photo=image, caption=caption, reply_markup=keyboard.view_handler(
        name, artist_uri, list_of_albums, list_of_singles))
    bot.pin_chat_message(message.chat.id, pin.id)
@retry_func
def send_song_data(message):
    text_message = message.text
    if "," not in message.text:
        text_message = message.text + ","
    data_list = text_message.split(",")
    song = data_list[0]
    try:
        artist = data_list[1]
    except BaseException:
        artist = ""
    artist, preview_url, release_date, album, track_no, total_tracks, image, id = spotify.get_track_details(
        artist, song)
    caption = f"👤Artist: {artist}\n🎵Song : {song.title()}\n━━━━━━━━━━━━\n📀Album : {album}\n🔢Track : {track_no} of {total_tracks}\n⭐️ Released: {release_date}"
    send_audios_or_previews(preview_url, image, caption,
                            song, id, artist, message.chat.id, True)
@retry_func
def send_audios_or_previews(
        preview_url, image, caption, name, id, artist, chat_id, send_photo):
    track_url = f"{base_url}{id}"
    if send_photo:
        time.sleep(1.5)
        bot.send_photo(chat_id, photo=image, caption=caption,
                       reply_markup=keyboard.lyrics_handler(artist, name))
    update = bot.send_message(chat_id, "... Downloading song just a sec ...")
    artist, preview_url, release_date, album, track_no, total_tracks, image, track_id = spotify.get_track_details(
        artist, name)
    query = f"{name} {artist}"
    data = audio.download_webm(f"{query}", name)
    bot.edit_message_text("Adding metadata😇...", chat_id, update.id)
    if data is not None:
        files = [f for f in os.listdir(
            '.') if os.path.isfile(f) and f.endswith('.mp3')]
        # artist,artist,release_date,album,name,track_no,image,files[0]
        audio.set_metadata(artist, release_date, album,
                           name, track_no, image, files[0])
        path = files[0]
        with open(path, "rb") as file:
            bot.send_chat_action(chat_id, "upload_audio")
            bot.send_audio(chat_id, audio=file, title=f'{name}', performer=artist,
                           reply_markup=keyboard.start_markup, caption="@JonaAtong")
        os.remove(path)
    elif preview_url is None:
        bot.send_message(chat_id, text=f"{track_url}")
    else:
        response = requests.get(preview_url)
        audio_content = response.content
        audio_io = BytesIO(audio_content)
        bot.send_chat_action(chat_id, "upload_audio")
        bot.send_audio(chat_id, audio=audio_io,
                       title=f'{name}', performer=artist, reply_markup=keyboard.start_markup)
    bot.delete_message(chat_id, update.id)


def get_album_songs(small_uri, chat_id, list_of_albums):
    for idx, album in enumerate(list_of_albums):
        if small_uri in album['uri'].split(":")[2]:
            album_name = album["name"]
            chosen_album = album
    release_date, total_tracks, photo, track_list = spotify.get_album_details(
        small_uri)
    caption = f"📀 Album: {album_name}\n⭐️ Released: {release_date}\n🔢 Total Tracks: {total_tracks}"
    bot.send_photo(chat_id, photo, caption=caption)
    album_tracks = spotify.get_album_tracks(chosen_album["uri"])
    for track in album_tracks:
        name = track['name']
        artist = track["artist"]
        artist, preview_url, release_date, album, track_no, total_tracks, image, id = spotify.get_track_details(
            artist, name)
        caption = f"👤Artist: {artist}\n🔢Track : {track_no} of {total_tracks}\n🎵Song : {name}\n"
        send_audios_or_previews(
            preview_url, photo, caption, name, id, artist, chat_id, False)

    bot.send_message(
        chat_id, f'Those are all the {total_tracks} track(s) by {artist} in "{album_name}" 💪!', reply_markup=keyboard.start_markup)


def get_top_tracks(chat_id, uri):
    top_tracks_data = spotify.artist_top_tracks(uri, spotify.no_of_songs)
    track_names = top_tracks_data[0]
    track_details = []
    tracks_data = top_tracks_data[1]
    for track in tracks_data:
        uri = track["uri"]
        id = track["id"]
        name = track["name"]
        artist = track["artists"][0]["name"]
        artist, preview_url, release_date, album, track_no, total_tracks, image, id = spotify.get_track_details(
            artist, name)
        dict = {
            "name": name,
            "preview_url": preview_url,
            "image": image,
            "release_date": release_date,
            "album": album,
            'track_no': track_no,
            "total_tracks": total_tracks
        }
        track_details.append(dict)
        caption = f"👤 Artist : {artist}\n🎵 Song : {name}\n━━━━━━━━━━━━\n📀Album : {album}\n🔢 Track : {track_no} of {total_tracks}\n⭐️ Released: {release_date}"
        send_audios_or_previews(
            preview_url, image, caption, name, id, artist, chat_id, True)
    bot.send_message(
        chat_id, f"Those are {artist}'s top 🔝 {spotify.no_of_songs} tracks 💪!", reply_markup=keyboard.start_markup)


def send_checker(artist_id, type, list_of_type, chat_id):
    make = bot.send_message(chat_id, "Awesome which ones tracks do you want to get?",
                            reply_markup=keyboard.make_for_type(artist_id, type, list_of_type))
    make_dict = {"name": 'make', "keyboard": make}
    keyboards_list.append(make_dict)


@bot.message_handler(commands=['start'])
def welcome(message):
    add_chat_user(message.chat.id, message.from_user.first_name,
                  message.from_user.last_name, message.from_user.username)

    bot.send_message(message.chat.id, f"Hello {message.from_user.first_name}, Welcome to Spotify SG✨'s bot!. For help see commands?👉 /commands",
                     reply_markup=keyboard.start_markup)


@bot.message_handler(commands=['commands'])
def info(message):
    bot.reply_to(
        message, "/start - Starts the bot\n/song - Search for a song\n/artist - Search for an artist\n/lyrics - Get lyrics of a song")
# /topsongs - Get top 10 tracks in the world")


@bot.message_handler(commands=['status'])
def status(message):
    bot.reply_to(message, "I am awake😏.")


def send_lyrics(message):
    send_song_data(message)
    text_message = message.text
    if "," not in message.text:
        text_message = message.text + ","
    data_list = text_message.split(",")
    title = data_list[0]
    try:
        artist = data_list[1]
    except BaseException:
        artist = ""
    artist, preview_url, release_date, album, track_no, total_tracks, image, id = spotify.get_track_details(
        artist, title)
    lyrics = extract_lyrics.get_lyrics(f"{title} {artist}")["lyrics"]
    caption = f"👤Artist: {artist}\n🎵Song : {title.title()}\n━━━━━━━━━━━━\n📀Album : {album}\n🔢Track : {track_no} of {total_tracks}\n⭐️ Released: {release_date}\n\n🎶Lyrics:\n{lyrics}"
    try:
        bot.send_message(message.chat.id, text=caption)
    except BaseException:
        splitted_text = util.smart_split(caption, chars_per_string=3000)
        for text in splitted_text:
            bot.send_message(message.chat.id, text=text)


@bot.message_handler(commands=['lyrics'])
def handle_lyrics(message):
    bot.send_message(
        message.chat.id, "Awesome, send me the name of the song with the artist separated by a comma")
    bot.register_next_step_handler_by_chat_id(
        message.chat.id, lambda msg: send_lyrics(msg))


@bot.message_handler(commands=["artist"])
def artist(message):
    bot.send_message(message.chat.id, "Send me the name of the artist",
                     reply_markup=keyboard.force_markup)
    bot.register_next_step_handler_by_chat_id(
        message.chat.id, lambda msg: search_artist(msg))


# @bot.message_handler(commands=['topsongs'])
# def topsongs(message):
#     bot.send_message(message.chat.id, "typing")
#     titles, artists = spotify.get_data(spotify.no_of_songs)
#     for index in range(0, spotify.no_of_songs):
#         artist = artists[index]
#         song = titles[index]

#         return
#         artist, preview_url, release_date, album, track_no, total_tracks,image = get_track_details(id)
#         caption = f"👤Artist: {artist}\n🎵Song : {song}\n━━━━━━━━━━━━\n📀Album : {album}\n🔢Track : {track_no} of {total_tracks}\n⭐️ Released: {release_date}"
#         send_audios_or_previews(preview_url, image, caption, song, id, artist, message.chat.id,True)
#     bot.send_message(message.chat.id, f"Those are the top 🔝 {no_of_songs} biggest hits of this week 💪!",
#                      reply_markup=start_markup)
@bot.message_handler(commands=['ping'])
def ping(message):
    start_time = time.time()
    response = bot.send_message(message.chat.id, "Pinging...")
    end_time = time.time()
    elapsed_time_ms = int((end_time - start_time) * 1000)
    
    bot.edit_message_text(f"Pong! 🏓\nResponse Time: {elapsed_time_ms} ms", message.chat.id, response.message_id)

@bot.message_handler(commands=['speed'])
def speed(message):
    run = bot.send_message(message.chat.id, "Running speedtest ...")
    text = get_speed()
    bot.edit_message_text(text,message.chat.id, run.message_id)
@bot.message_handler(commands=["song"])
def get_song(message):
    bot.send_message(message.chat.id, "Awesome, send the name of the song with the artist separated by a comma",
                     reply_markup=keyboard.force_markup)
    bot.register_next_step_handler_by_chat_id(
        message.chat.id, lambda message: send_song_data(message))


@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text == "hello":
        bot.send_message(message.chat.id, f"Hi {message.from_user.firstname}")
    elif message.text == "⬆️ Show command buttons":
        bot.send_message(message.chat.id, "⬆️ Show command buttons",
                         reply_markup=keyboard.start_markup)
    elif message.text == "⬇️ Hide command buttons":
        bot.send_message(message.chat.id, "⬇️ Hide command buttons",
                         reply_markup=keyboard.hide_keyboard)


@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data.startswith('album_'):
        uri = call.data.split('_')[1]
        chat_id = call.message.chat.id
        list_of_type = spotify.get_artist_albums((uri), 'album')
        send_checker(uri, "album", list_of_type, chat_id)
    if call.data.startswith('single_'):
        uri = call.data.split('_')[1]
        chat_id = call.message.chat.id
        list_of_type = spotify.get_artist_albums((uri), 'single')
        send_checker(uri, "single", list_of_type, chat_id)
    elif call.data.startswith("track_"):
        uri = call.data.split('_')[1]
        get_top_tracks(call.message.chat.id, uri)
    elif call.data.startswith("lyrics_"):
        title = call.data.split("_")[1]
        artist = call.data.split("_")[2]
        artist, preview_url, release_date, album, track_no, total_tracks, image, id = spotify.get_track_details(
            artist, title)
        lyrics = extract_lyrics.get_lyrics(f"{title} {artist}")["lyrics"]
        caption = f"👤Artist: {artist}\n🎵Song : {title.title()}\n━━━━━━━━━━━━\n📀Album : {album}\n🔢Track : {track_no} of {total_tracks}\n⭐️ Released: {release_date}\n\n🎶Lyrics:\n{lyrics}"
        try:
            bot.send_message(call.message.chat.id, text=caption)
        except BaseException:
            splitted_text = util.smart_split(caption, chars_per_string=3000)
            for text in splitted_text:
                bot.send_message(call.message.chat.id, text=text)
    elif call.data.startswith("close"):
        off = call.data.split("_")[1]
        if off == "make":
            for board in keyboards_list:
                if board["name"] == 'make':
                    keyboards_list.remove(board)
                    bot.delete_message(call.message.chat.id,
                                       board["keyboard"].id)
                if board["name"] == 'handler':
                    bot.delete_message(call.message.chat.id,
                                       board["keyboard"].id)
    else:
        split_data = call.data.split('_')
        if len(split_data) >= 3:
            small_id = split_data[0]
            type = split_data[1]
            small_uri = split_data[2]
            list_of_type = spotify.get_artist_albums(small_id, type)
            get_album_songs(small_uri, call.message.chat.id, list_of_type)

if __name__ == '__main__':
    print("Bot is running 👌")
    bot.polling()
