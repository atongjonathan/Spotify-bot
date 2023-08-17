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

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot((TELEGRAM_BOT_TOKEN))

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


def send_data(tg_bot, msg):
    tg_bot.send_chat_action(msg.chat.id, "typing")
    message = msg.text.lower()
    file = get_scores(message)
    text = ''.join(file)
    try:
        tg_bot.send_message(msg.chat.id,
                            f"{text}\nSource: https://www.livescore.cz", reply_markup=start_markup)
        tg_bot.send_message(msg.chat.id, "Refresh: /livescores")
    except:
        splitted_text = util.smart_split(text, chars_per_string=3000)
        for text in splitted_text:
            tg_bot.send_message(msg.chat.id, text)
        tg_bot.send_message(msg.chat.id, "Refresh: /livescores", reply_markup=start_markup)


@bot.message_handler(commands=['livescores'])
def livescores(message):
    bot.send_message(message.chat.id, "Choose a sport", reply_markup=sport)

    bot.register_next_step_handler_by_chat_id(message.chat.id,
                                              lambda msg: send_data(bot, msg))

@bot.message_handler(commands=["artist"])
def artist(message):
    bot.send_message(message.chat.id, "Send me the name of the artist", reply_markup=force_markup)
    bot.register_next_step_handler_by_chat_id(message.chat.id,lambda msg : search(msg))

# @bot.message_handler(commands=[''])
def search(message):
    uri,followers,images,name,genres = get_details_artist(message.text)
    image = images[0]
    genres = [item.title() for item in genres]
    artist_albums_info = get_artist_albums(uri)
    artist_albums = []
    for album in enumerate(artist_albums_info):
        artist_albums.append(album)
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
    for dict in list_of_albums:
        names.append(str(dict['index']+1)+'. '+str(dict['name'])+"\n")
        uris.append(dict["uri"])
    text = f"👤Artist: {name}\n🧑Followers: {followers:,} \n🎵Genre(s): {', '.join(genres)} \n📀 Albums:\n       {'       '.join(names)}"
    list_of_tracks = []
    bot.send_photo(message.chat.id, photo=image, caption=text)
    bot.send_message(message.chat.id, f"Get all tracks of any of {name}'s albums?",reply_markup=yes_no_keyboard)
    bot.register_next_step_handler_by_chat_id(message.chat.id, lambda msg: check(msg,list_of_albums,list_of_tracks))
def send_checker(message,list_of_albums,list_of_tracks):
    if len(list_of_tracks)==0:
        if message.text == "Yes":
            bot.send_message(message.chat.id,"Awesome which album's tracks do you ant to get?", reply_markup=create_album_keyboard(list_of_albums,list_of_tracks))
            bot.register_next_step_handler_by_chat_id(message.chat.id, lambda msg : get_album_songs(msg, list_of_albums))
        elif message.text == "No":
            bot.send_message(message.chat.id, "Done artist search complete",reply_markup=start_markup)
def check(message,list_of_albums,list_of_tracks):
    send_checker(message,list_of_albums,list_of_tracks)

def get_album_songs(message, list_of_albums):
    for album in list_of_albums:
        if message.text == album["name"]:
            chosen_album = album
    album_tracks = get_album_tracks(chosen_album["uri"])
    track_list = []
    for idx,track in enumerate(album_tracks):
        data = f"{idx+1}. {track['name']}"+"\n"
        track_list.append(data)
    release_date,total_tracks,photo = get_album_cover_art(chosen_album["uri"])
    tracks =f"{'       '.join(track_list)}"
    caption = f"📀 Album: {message.text}\n⭐️ Released: {release_date}\nTotal Tracks: {total_tracks}\nTracks:\n       {tracks}"
    bot.send_photo(message.chat.id,photo=photo, caption=caption, reply_markup=start_markup)

def send_album_tracks(message,list_of_tracks):
    bot.send_message(message.chat.id, "".join(list_of_tracks))
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
        # song_id = search_song_id(artist,song)
        # preview_url = get_preview_url(song_id)
        image = get_track_image(id)
        replace = [","," ", "&", ".", "Featuring"]
        for item in replace:
            if item in artist:
                artist = artist.replace(item, "")
        caption = f"👤Artist #{artist}\n🎵Song : {song}\n━━━━━━━━━━━━\n📀Album : {album}\n🔢Track : {track_no} of {total_tracks}\n⭐️ Released: {release_date}"
        bot.send_photo(message.chat.id,photo=image,caption=caption)
        if preview_url is not None:
            response = requests.get(preview_url)
            audio_content = response.content
            audio_io = BytesIO(audio_content)
            bot.send_audio(chat_id=message.chat.id, audio=audio_io, title=f'{song}', performer=artist,reply_markup=start_markup)
        else:
            bot.send_message(message.chat.id, "Audio preview was not found")
        # time.sleep(1.5)
    bot.send_message(message.chat.id, f"Those are the top 🔝 {no_of_songs} biggest hits of this week 💪!",reply_markup=start_markup)


@bot.message_handler(commands=['ig_followers_game'])
def begin(message):
    bot.send_message(
        message.chat.id,
        " Please answer with '🅰' or '🅱:'. \nEnter 's's to stop the game and see your final score😉",
        reply_markup=keyboard)
    ig_game = IgFollowers()
    ig_game.ask_question(bot, message.chat.id, keyboard)


@bot.message_handler(commands=["song"])
def get_song(message):
    bot.send_message(message.chat.id, "Send me the name of the song followed by a comma then the name of the artist. Example: It ain't me , Kygo \nIf artist is not known leave blank after the comma Example: It ain't me ,",reply_markup=force_markup)
    bot.register_next_step_handler_by_chat_id(message.chat.id, lambda message:done(message))
def done(message):
    if "," not in message.text:
        bot.send_message(message.chat.id, "No comma found, try again")
        get_song(message)
    data_list = message.text.split(",")
    song = data_list[0]
    try:
        artist = data_list[1]
    except:
        artist = ""
    id = get_track_id(artist,song)
    artist, preview_url, release_date, album, track_no,total_tracks = get_track_details(id)
    image = get_track_image(id)
    replace = [","," ", "&", ".", "Featuring"]
    for item in replace:
            if item in artist:
                artist = artist.replace(item, "")
    caption = f"👤Artist #{artist}\n🎵Song : {song.title()}\n━━━━━━━━━━━━\n📀Album : {album}\n🔢Track : {track_no} of {total_tracks}\n⭐️ Released: {release_date}"
    bot.send_photo(message.chat.id,photo=image,caption=caption)
    if preview_url is not None:
        response = requests.get(preview_url)
        audio_content = response.content
        audio_io = BytesIO(audio_content)
        bot.send_audio(chat_id=message.chat.id, audio=audio_io, title=song, performer=artist, reply_markup=start_markup)
    else:
        bot.send_message(message.chat.id, "Audio preview was not found", reply_markup=start_markup)


@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text == "hello":
        bot.send_message(message.chat.id, f"Hi {message.from_user.firstname}" )
    elif message.text == "⬆️ Show command buttons":
        bot.send_message(message.chat.id, "⬆️ Show command buttons",reply_markup=start_markup)
    elif message.text == "⬇️ Hide command buttons":
        bot.send_message(message.chat.id, "⬇️ Hide command buttons",reply_markup=hide_keyboard)
 




print("Bot is on>>>>")
bot.polling()
