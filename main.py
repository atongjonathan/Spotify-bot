import telebot
import random
from info import quotes
from ig_followers import IgFollowers
from livescore import get_scores
from top_songs import get_data
from telebot import util
from keyboards import *
from spotify import *
import requests,os
from io import BytesIO
import time

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot((TELEGRAM_BOT_TOKEN))
base_url = "https://open.spotify.com/track/"

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id ,f"Hello {message.from_user.first_name}, Welcome to SG✨'s bot😅!", reply_markup=start_markup)

@bot.message_handler(commands=['help'])
def help(message):
    bot.reply_to(
        message,
        "Here are some available commands for now: /start, /commands, /quote, /ig_followers_game, /help, /info, /status"
    )


@bot.message_handler(commands=['info'])
def info(message):
    bot.reply_to(message, "Developer: @JonaAtong™.")


@bot.message_handler(commands=['status'])
def status(message):
    bot.reply_to(message, "I am awake😏.")


@bot.message_handler(commands=['quote'])
def quote(message):
    today_quote = random.choice(quotes)
    bot.reply_to(message, f"{(today_quote)}")



@bot.message_handler(commands=["artist"])
def artist(message):
    global chat_id
    chat_id = message.chat.id
    bot.send_message(message.chat.id, "Send me the name of the artist", reply_markup=force_markup)
    bot.register_next_step_handler_by_chat_id(message.chat.id,lambda msg : search(msg))




    pass
def search(message):
    uri,followers,images,name,genres = get_details_artist(message.text)
    global uri_ar
    uri_ar = uri
    image = images[0]
    genres = [item.title() for item in genres]
    artist_albums_info = get_artist_albums(uri)
    artist_albums = []
    for album in enumerate(artist_albums_info):
        artist_albums.append(album)
    global list_of_albums
    list_of_albums = []
    for item in artist_albums:
        dict = {
            'index': item[0],
            "name" : item[1]["name"],
            "uri": item[1]["uri"]
        }
        list_of_albums.append(dict)
    names = []
    uris = []
    handler = get_handler_of_artist(message.text,list_of_albums)
    for dict in list_of_albums:
        names.append(str(dict['index']+1)+'. '+str(dict['name'])+"\n")
        uris.append(dict["uri"])
    text = f"👤Artist: {name}\n🧑Followers: {followers:,} \n🎵Genre(s): {', '.join(genres)} \n📀 Albums:\n       {'       '.join(names)}"
    list_of_tracks = []
    bot.send_photo(message.chat.id, photo=image, caption=text, reply_markup=handler)
 
@bot.callback_query_handler(func=lambda call:True)
def handle_query(call):
    if call.data.startswith('album_'):
        text = call.data.split('_')[1]
        send_checker(call.message.chat.id,list_of_albums)
    elif call.data.startswith("track_"):
        get_top_tracks(call.message.chat.id,uri_ar)
def send_checker(id,list_of_albums):
    bot.send_message(id,"Awesome which album's tracks do you want to get?", reply_markup=create_album_keyboard(list_of_albums))
    bot.register_next_step_handler_by_chat_id(id, lambda msg : get_album_songs(msg, list_of_albums))


def get_album_songs(msg, list_of_albums):
    for album in list_of_albums:
        if msg.text== album["name"]:
            album_name = album["name"]
            chosen_album = album
    release_date,total_tracks,photo = get_album_cover_art(chosen_album["uri"])
    caption = f"📀 Album: {album_name}\n⭐️ Released: {release_date}\n🔢 Total Tracks: {total_tracks}"
    bot.send_photo(chat_id,photo=photo, caption=caption, reply_markup=start_markup)
    album_tracks = get_album_tracks(chosen_album["uri"])
    for track in album_tracks:
        name = track['name']
        id = track['id']
        artist, preview_url, release_date, album, track_no,total_tracks = get_track_details(id)
        caption = f"👤Artist: {artist}\n🔢Track : {track_no} of {total_tracks}\n🎵Song : {name}\n"        
        if preview_url is not None:
            response = requests.get(preview_url)
            audio_content = response.content
            audio_io = BytesIO(audio_content)
            bot.send_message(msg.chat.id,text=caption)
            bot.send_audio(chat_id=msg.chat.id, audio=audio_io, title=f'{name}', performer=artist,reply_markup=start_markup)
        else:
            bot.send_message(msg.chat.id, text=f"{caption}\n{base_url}{id}")

    bot.send_message(msg.chat.id, f"Those are all the {total_tracks} tracks in {artist}'s {album_name} album 💪!",reply_markup=start_markup)

def get_top_tracks(id,uri):
    top_tracks_data = artist_top_tracks(uri, no_of_songs)
    track_names = top_tracks_data[0]
    track_details = []
    tracks_data = top_tracks_data[1]
    for idx,track in enumerate(tracks_data):
        uri = track["uri"]
        name = track["name"]
        image = get_track_image(uri)
        artist, preview_url, release_date, album, track_no,total_tracks = get_track_details(uri)
        dict = {
            "name":name,
            "preview_url": preview_url,
            "image": image,
            "release_date": release_date,
            "album": album,
            'track_no':track_no,
            "total_tracks":total_tracks
        }
        track_details.append(dict)
        caption = f"👤 Artist : {artist}\n🎵 Song : {name}\n━━━━━━━━━━━━\n📀Album : {album}\n🔢 Track : {track_no} of {total_tracks}\n⭐️ Released: {release_date}"
        if preview_url is not None:
            response = requests.get(preview_url)
            audio_content = response.content
            audio_io = BytesIO(audio_content)
            bot.send_audio(chat_id=id, audio=audio_io, title=f'{name}', performer=artist,reply_markup=start_markup)
        else:
            uri_parts = uri.split(":")
            track_id = uri_parts[-1]
            bot.send_message(chat_id=id,text=f"{caption}\n{base_url}{track_id}")            
    bot.send_message(id, f"Those are {artist}'s top 🔝 {no_of_songs} top tracks 💪!",reply_markup=start_markup)



@bot.message_handler(commands=['topsongs'])
def topsongs(message):
    no_of_songs = 10
    bot.send_chat_action(message.chat.id, "typing")
    titles, artists = get_data(no_of_songs)
    for index in range(0, no_of_songs):
        artist = artists[index]
        song = titles[index]
        id = get_track_id(artist,song)
        artist,preview_url, release_date, album, track_no,total_tracks = get_track_details(id)
        image = get_track_image(id)
        caption = f"👤Artist: {artist}\n🎵Song : {song}\n━━━━━━━━━━━━\n📀Album : {album}\n🔢Track : {track_no} of {total_tracks}\n⭐️ Released: {release_date}"
        bot.send_photo(message.chat.id,photo=image,caption=caption)
        if preview_url is not None:
            response = requests.get(preview_url)
            audio_content = response.content
            audio_io = BytesIO(audio_content)
            bot.send_audio(chat_id=message.chat.id, audio=audio_io, title=f'{song}', performer=artist,reply_markup=start_markup)
        else:
            bot.send_message(message.chat.id, f"{base_url}{id}")
    bot.send_message(message.chat.id, f"Those are the top 🔝 {no_of_songs} biggest hits of this week 💪!",reply_markup=start_markup)



@bot.message_handler(commands=["song"])
def get_song(message):
    bot.send_message(message.chat.id, "Send me the name of the song followed by a comma and finally the name of the artist.", reply_markup=force_markup)
    bot.register_next_step_handler_by_chat_id(message.chat.id, lambda message:done(message))
def done(message):
    text_message = message.text
    if "," not in message.text:
        text_message = message.text+","
    data_list = text_message.split(",")
    song = data_list[0]
    try:
        artist = data_list[1]
    except:
        artist = ""
    id = get_track_id(artist,song)
    artist, preview_url, release_date, album, track_no,total_tracks = get_track_details(id)
    image = get_track_image(id)
    caption = f"👤Artist: {artist}\n🎵Song : {song.title()}\n━━━━━━━━━━━━\n📀Album : {album}\n🔢Track : {track_no} of {total_tracks}\n⭐️ Released: {release_date}"
    if preview_url is not None:
        bot.send_photo(message.chat.id,photo=image,caption=caption, reply_markup=start_markup)
        response = requests.get(preview_url)
        audio_content = response.content
        audio_io = BytesIO(audio_content)
        bot.send_audio(chat_id=message.chat.id, audio=audio_io, title=song, performer=artist, reply_markup=start_markup)
    else:
        bot.send_message(message.chat.id, text=f"{caption}\n{base_url}{id}", reply_markup=start_markup)        


@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text == "hello":
        bot.send_message(message.chat.id, f"Hi {message.from_user.firstname}" )
    elif message.text == "⬆️ Show command buttons":
        bot.send_message(message.chat.id, "⬆️ Show command buttons",reply_markup=start_markup)
    elif message.text == "⬇️ Hide command buttons":
        bot.send_message(message.chat.id, "⬇️ Hide command buttons",reply_markup=hide_keyboard)






print("Bot is on>>>>")
try:
    bot.polling()
except Exception as e:
    print(e)
    bot.polling()
