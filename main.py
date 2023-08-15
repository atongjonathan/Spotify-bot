import telebot
import random
from info import quotes, logo
from ig_followers import IgFollowers
from livescore import get_scores
from top_songs import get_data
from telebot import util
import html
from keyboards import keyboard,sport,start_markup
from spotify import get_cover_art,search_song_id,get_track_coverart,get_preview_url
import requests,os
from io import BytesIO

bot = telebot.TeleBot(("6523079919:AAGwY9wKIY7p_dHN7sOjtyacZS5SgsEUF5w"))

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



@bot.message_handler(commands=['topsongs'])
def topsongs(message):
    no_of_songs = 20
    bot.send_chat_action(message.chat.id, "typing")
    titles, artists = get_data(no_of_songs)
    for index in range(0, no_of_songs):
        artist = artists[index]
        song = titles[index]
        text = f"{song} - {artist}"
        # image = get_artist_image()
        song_id = search_song_id(artist,song)
        preview_url = get_preview_url(song_id)
        image = get_track_coverart(song_id)
        bot.send_photo(message.chat.id,photo=image,caption=f'{index+1}. {text}')
        if preview_url is not None:
            response = requests.get(preview_url)
            audio_content = response.content
            audio_io = BytesIO(audio_content)
            bot.send_audio(chat_id=message.chat.id, audio=audio_io, title=text, performer=artist)
        else:
            bot.send_message(message.chat.id, "Audio preview was not found")
        # time.sleep(1.5)
    bot.send_message(message.chat.id, f"Those are the top 🔝 {no_of_songs} biggest hits of this week 💪!",reply_markup=start_markup)


@bot.message_handler(commands=['ig_followers_game'])
def begin(message):
    bot.send_message(message.chat.id, f"{logo}")
    # with open("giphy.mp4", "rb") as file:
    #     bot.send_document(document=file, chat_id=message.chat.id)
    bot.send_message(
        message.chat.id,
        " Please answer with '🅰' or '🅱:'. \nEnter 's's to stop the game and see your final score😉",
        reply_markup=keyboard)
    ig_game = IgFollowers()
    ig_game.ask_question(bot, message.chat.id, keyboard)

print("Bot is on>>>>")
bot.polling()
