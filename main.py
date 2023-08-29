import telebot
import random
from info import quotes
from top_songs import get_data
from keyboards import *
from spotify import *
import requests, os
from io import BytesIO
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot((TELEGRAM_BOT_TOKEN))
base_url = "https://open.spotify.com/track/"
MAX_RETRIES = 10
def retry_func(func):
    def wrapper(*args, **kwargs):
        retries = 0
        while retries < MAX_RETRIES:
            try:
                return func(*args, **kwargs)
            except ConnectionError as e:
                date = datetime.now().strftime("%d %M %Y at %H %M %S")
                print(f"Error {retries},{e} {date} \n Retrying...")
                retries += 1
            except Exception as e:
                print(f"Error {retries},{e} {date} \n Retrying...")
        print("Max Retries reached")
        return None
    return wrapper
chat_user_data = {0}

# Add a new chat and user to the dictionary
def add_chat_user(chat_id, fname, lname, uname):
    date = datetime.now().strftime("%d %M %Y at %H %M %S")
    print(f"{fname} {lname} @{uname} accessed\n chat -{chat_id} at {date}")
    # with open("data/names.txt", 'a') as file:
    #     file.write(f"\n{fname}, {lname}, {uname}")
    # with open("data/chats.txt", 'a') as file:
    #     file.write(f"\n{chat_id}")
@retry_func
def search(message):
    artist_uri, followers, images, name, genres = get_details_artist(message.text)
    try:
        image = images[0]
    except IndexError:
        image = "https://cdn.business2community.com/wp-content/uploads/2014/03/Unknown-person.gif"
    genres = [item.title() for item in genres]
    list_of_albums = get_artist_albums(artist_uri, "album")
    list_of_singles = get_artist_albums(artist_uri,"single")
    album_names = []
    ep_names = []
    for index,dict in enumerate(list_of_singles):
        ep_names.append(str(index + 1) + '. ' + str(dict['name']) + "\n")
    for index,dict in enumerate(list_of_albums):
        album_names.append(str(index + 1) + '. ' + str(dict['name']) + "\n")

    caption = f"👤Artist: {name}\n🧑Followers: {followers:,} \n🎭Genre(s): {', '.join(genres)} \n"
    bot.send_photo(message.chat.id, photo=image, caption=caption, reply_markup=handler(name,artist_uri,list_of_albums,list_of_singles))

@retry_func
def done(message):
    text_message = message.text
    if "," not in message.text:
        text_message = message.text + ","
    data_list = text_message.split(",")
    song = data_list[0]
    try:
        artist = data_list[1]
    except:
        artist = ""
    id = get_track_id(artist, song)
    artist, preview_url, release_date, album, track_no, total_tracks = get_track_details(id)
    image = get_track_image(id)
    caption = f"👤Artist: {artist}\n🎵Song : {song.title()}\n━━━━━━━━━━━━\n📀Album : {album}\n🔢Track : {track_no} of {total_tracks}\n⭐️ Released: {release_date}"
    send_audios_or_previews(preview_url, image, caption, song, id, artist, message.chat.id,True)
def send_audios_or_previews(preview_url, image, caption, name, id, artist, chat_id,send_photo):
    if send_photo:
        bot.send_photo(chat_id, photo=image, caption=caption, reply_markup=start_markup)
    if preview_url is None :
        bot.send_message(chat_id, text=f"{caption}\n{base_url}{id}")
    else:
        response = requests.get(preview_url)
        audio_content = response.content
        audio_io = BytesIO(audio_content)
        bot.send_audio(chat_id, audio=audio_io, title=f'{name}', performer=artist, reply_markup=start_markup)

def get_album_songs(small_uri,chat_id, list_of_albums):
    for idx, album in enumerate(list_of_albums):
        if small_uri in album['uri'].split(":")[2]:
            album_name = album["name"]
            chosen_album = album
    release_date, total_tracks, photo = get_album_cover_art(small_uri)
    caption = f"📀 Album: {album_name}\n⭐️ Released: {release_date}\n🔢 Total Tracks: {total_tracks}"
    bot.send_photo(chat_id,photo,caption=caption)
    album_tracks = get_album_tracks(chosen_album["uri"])
    for track in album_tracks:
        name = track['name']
        id = track['id']
        artist, preview_url, release_date, album, track_no, total_tracks = get_track_details(id)
        caption = f"👤Artist: {artist}\n🔢Track : {track_no} of {total_tracks}\n🎵Song : {name}\n"
        send_audios_or_previews(preview_url, photo, caption, name, id, artist, chat_id,False)

    bot.send_message(chat_id, f"Those are all the {total_tracks} tracks in {artist}'s {album_name} 💪!",reply_markup=start_markup)


def get_top_tracks(chat_id, uri):
    top_tracks_data = artist_top_tracks(uri, no_of_songs)
    track_names = top_tracks_data[0]
    track_details = []
    tracks_data = top_tracks_data[1]
    for track in tracks_data:
        uri = track["uri"]
        id = track["id"]
        name = track["name"]
        image = get_track_image(uri)
        artist, preview_url, release_date, album, track_no, total_tracks = get_track_details(uri)
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
        send_audios_or_previews(preview_url, image, caption, name, id, artist, chat_id,True)
    bot.send_message(chat_id, f"Those are {artist}'s top 🔝 {no_of_songs} top tracks 💪!", reply_markup=start_markup)




def send_checker(artist_id ,type, list_of_type, chat_id):
    bot.send_message(chat_id, "Awesome which ones tracks do you want to get?",
                     reply_markup=make_for_type(artist_id,type,list_of_type))


@bot.message_handler(commands=['start'])
def welcome(message):
    add_chat_user(message.chat.id,message.from_user.first_name, message.from_user.last_name,message.from_user.username)

    bot.send_message(message.chat.id, f"Hello {message.from_user.first_name}, Welcome to SG✨'s bot😅!",
                     reply_markup=start_markup)


# @bot.message_handler(commands=['info'])
# def info(message):
#     bot.reply_to(message, "Developer: @JonaAtong™.")


@bot.message_handler(commands=['status'])
def status(message):
    bot.reply_to(message, "I am awake😏.")


@bot.message_handler(commands=['quote'])
def quote(message):
    today_quote = random.choice(quotes)
    bot.reply_to(message, f"{(today_quote)}")


@bot.message_handler(commands=["artist"])
def artist(message):
    bot.send_message(message.chat.id, "Send me the name of the artist", reply_markup=force_markup)
    bot.register_next_step_handler_by_chat_id(message.chat.id, lambda msg: search(msg))



@bot.message_handler(commands=['topsongs'])
def topsongs(message):
    no_of_songs = 10
    bot.send_chat_action(message.chat.id, "typing")
    titles, artists = get_data(no_of_songs)
    for index in range(0, no_of_songs):
        artist = artists[index]
        song = titles[index]
        id = get_track_id(artist, song)
        artist, preview_url, release_date, album, track_no, total_tracks = get_track_details(id)
        image = get_track_image(id)
        caption = f"👤Artist: {artist}\n🎵Song : {song}\n━━━━━━━━━━━━\n📀Album : {album}\n🔢Track : {track_no} of {total_tracks}\n⭐️ Released: {release_date}"
        send_audios_or_previews(preview_url, image, caption, song, id, artist, message.chat.id,True)
    bot.send_message(message.chat.id, f"Those are the top 🔝 {no_of_songs} biggest hits of this week 💪!",
                     reply_markup=start_markup)


@bot.message_handler(commands=["song"])
def get_song(message):
    bot.send_message(message.chat.id,
                     "Send me the name of the song followed by a comma and finally the name of the artist.",
                     reply_markup=force_markup)
    bot.register_next_step_handler_by_chat_id(message.chat.id, lambda message: done(message))




@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text == "hello":
        bot.send_message(message.chat.id, f"Hi {message.from_user.firstname}")
    elif message.text == "⬆️ Show command buttons":
        bot.send_message(message.chat.id, "⬆️ Show command buttons", reply_markup=start_markup)
    elif message.text == "⬇️ Hide command buttons":
        bot.send_message(message.chat.id, "⬇️ Hide command buttons", reply_markup=hide_keyboard)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data.startswith('album_'):
        uri = call.data.split('_')[1]
        chat_id = call.message.chat.id
        list_of_type = get_artist_albums((uri),'album')
        send_checker(uri,"album",list_of_type,chat_id)
    if call.data.startswith('single_'):
        uri = call.data.split('_')[1]
        chat_id = call.message.chat.id
        list_of_type = get_artist_albums((uri),'single')
        send_checker(uri,"single",list_of_type,chat_id)
    elif call.data.startswith("track_"):
        uri = call.data.split('_')[1]
        get_top_tracks(call.message.chat.id, uri)
    else:
        split_data = call.data.split('_')
        if len(split_data) >= 3:
            small_id = split_data[0]
            type = split_data[1]
            small_uri = split_data[2]
            list_of_type = get_artist_albums(small_id, type)
            get_album_songs(small_uri, call.message.chat.id, list_of_type)


print("Bot is running 👌")
bot.polling()
