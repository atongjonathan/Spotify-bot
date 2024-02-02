import time
import warnings
from logging import FileHandler, StreamHandler, INFO, basicConfig, getLogger
from bot import SGBot


basicConfig(
    format='SG-Bot | %(levelname)s | %(asctime)s - %(name)s - line %(lineno)d | %(message)s',
    handlers=[FileHandler('logs.txt'),
              StreamHandler()],
    level=INFO)
logger = getLogger(__name__)

sgbot = SGBot()
bot = sgbot.BOT


@bot.message_handler(commands=['start'])
def welcome(message):
    logger.info(
        f"{message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username} accessed Chat: {message.chat.id}"
    )
    bot.send_message(
        message.chat.id,
        f"Hello `{message.from_user.first_name}`, Welcome to Spotify SG✨'s bot!. For help see commands?👉 /commands",
        reply_markup=sgbot.keyboard.start_markup)


@bot.message_handler(commands=["artist"])
def artist(message):
    artist_reply = "Send me the name of the artist"
    sgbot.get_search_query(
        message, "artist", sgbot.search_artist, artist_reply)


@bot.message_handler(commands=["song"])
def song(message,):
    sgbot.isPreview = False
    song_reply = "Send me the song title followed by the artist separated by a comma for optimal results"
    sgbot.get_search_query(message, "song", sgbot.search_song, song_reply)


@bot.message_handler(commands=['trending'])
def trending(message):
    text = message.text
    if " " not in text:
        no_of_songs = 10
    else:
        no_of_songs = int(text.replace(f"/trending ", ""))
        if no_of_songs > 100:
            bot.reply_to(
                message, "Number requested to should be less than 100")
            return
    sgbot.search_trending(message, no_of_songs=no_of_songs)


@bot.message_handler(commands=['commands'])
def commands(message):
    bot.reply_to(
        message,
        "/start - Starts the bot\n/song - Search for a song\n/artist - Search for an artist\n/ping - Test Me"
    )


@bot.message_handler(commands=['logs'])
def logs(message):
    with open("logs.txt") as file:
        bot.send_document(message.chat.id, file,
                          reply_markup=sgbot.keyboard.start_markup)


@bot.message_handler(commands=['ping'])
def ping(message):
    start_time = time.time()
    response = bot.reply_to(message, "Pinging...")
    end_time = time.time()
    elapsed_time_ms = int((end_time - start_time) * 1000)

    bot.edit_message_text(f"Pong! 🏓\nResponse Time: `{elapsed_time_ms} ms`",
                          chat_id=message.chat.id,
                          message_id=response.message_id)


@bot.message_handler(commands=["snippet"])
def preview(message):
    sgbot.isPreview = True
    song_reply = "Send me the song title followed by the artist separated by a comma for optimal results"
    sgbot.get_search_query(message, "snippet", sgbot.search_song, song_reply)


@bot.message_handler(regexp="(https?:\\/\\/)?(www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{2,256}\\.[a-z]{2,6}\\b([-a-zA-Z0-9@:%_\\+.~#?&//=]*)?")
def regex(message):
    link = message.text
    mini_link = link.split("spotify.com/")[1].split("?")[0]
    link_type = mini_link.split("/")[0]
    uri = mini_link.split("/")[1]
    try:
        if link_type == 'album':
            sgbot.get_album_songs(uri, message.chat.id)
        elif link_type == 'track':
            track_details = sgbot.spotify.get_chosen_song(uri)
            sgbot.send_chosen_track(track_details, message.chat.id)
    except Exception as e:
        bot.reply_to(message, "Process unsuccessful! Check link or try again later")


@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text == "⬆️ Show command buttons":
        bot.reply_to(message,
                     "⬆️ Show command buttons",
                     reply_markup=sgbot.keyboard.start_markup)
    elif message.text == "⬇️ Hide command buttons":
        bot.reply_to(message,
                     "⬇️ Hide command buttons",
                     reply_markup=sgbot.keyboard.hide_keyboard)


# Set up a callback query handler
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    sgbot.process_callback_query(call)


if __name__ == '__main__':
    logger.info("Bot is running :>")
    bot.polling(non_stop=True)
