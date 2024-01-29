import time
import warnings
from logging import FileHandler, StreamHandler, INFO, basicConfig, getLogger
from utils import keyboard, bot, search_artist, send_song_data, process_callback_query
# from keep_alive import keep_alive
# import billboard



basicConfig(
    format='%(levelname)s | %(asctime)s - %(name)s - line %(lineno)d | %(message)s',
    handlers=[FileHandler('logs.txt'),
              StreamHandler()],
    level=INFO)
logger = getLogger(__name__)

# Filter out specific warnings from spotipy.cache_handler
warnings.filterwarnings("ignore")


@bot.message_handler(commands=['start'])
def welcome(message):
    logger.info(
        f"{message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username} accessed Chat: {message.chat.id}"
    )

    bot.send_message(
        message.chat.id,
        f"Hello `{message.from_user.first_name}`, Welcome to Spotify SG✨'s bot!. For help see commands?👉 /commands",
        reply_markup=keyboard.start_markup)


@bot.message_handler(commands=["artist"])
def artist(message):
    text = message.text
    if " " in text:
        artist = text.replace("/artist ", "")
        search_artist(message, artist)
    else:

        # Get the artist name from the user
        bot.reply_to(message,
                     "Send me the name of the artist",
                     reply_markup=keyboard.force_markup)
        # Parse the artist's name recieved from the user into the search artist
        # function
        bot.register_next_step_handler_by_chat_id(message.chat.id,
                                                  lambda msg: search_artist(msg))


@bot.message_handler(commands=["song"])
def get_song(message):
    text = message.text
    if " " in text:
        query = text.replace("/song ", "")
        send_song_data(message, query)
    else:
        bot.send_message(
            message.chat.id,
            "Awesome, send the name of the song with the artist separated by a comma for optimal results",
            reply_markup=keyboard.force_markup)
        bot.register_next_step_handler_by_chat_id(
            message.chat.id, lambda message: send_song_data(message))


# @bot.message_handler(commands=['trending'])
# def trending(message):
#     reply = bot.reply_to(message, "Getting trending songs ...")
#     hot_100 = billboard.ChartData("hot-100")
#     chart_data = []
#     for song in hot_100[:9]:
#         item = f"{song.title}, {song.artist}"
#         chart_data.append(item)
#     bot.edit_message_text("\n".join(chart_data), message.chat.id, reply.id)


@bot.message_handler(commands=['commands'])
def info(message):
    bot.reply_to(
        message,
        "/start - Starts the bot\n/song - Search for a song\n/artist - Search for an artist\n/ping - Test Me"
    )




@bot.message_handler(commands=['logs'])
def get_logs(message):
    file = open("logs.txt")
    bot.send_document(message.chat.id, file,
                      reply_markup=keyboard.start_markup)
    file.close()


@bot.message_handler(commands=['ping'])
def ping(message):
    start_time = time.time()
    response = bot.send_message(message.chat.id, "Pinging...")
    end_time = time.time()
    elapsed_time_ms = int((end_time - start_time) * 1000)

    bot.edit_message_text(f"Pong! 🏓\nResponse Time: `{elapsed_time_ms} ms`",
                          chat_id=message.chat.id,
                          message_id=response.message_id)


@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text == "⬆️ Show command buttons":
        bot.send_message(message.chat.id,
                         "⬆️ Show command buttons",
                         reply_markup=keyboard.start_markup)
    elif message.text == "⬇️ Hide command buttons":
        bot.send_message(message.chat.id,
                         "⬇️ Hide command buttons",
                         reply_markup=keyboard.hide_keyboard)


# Set up a callback query handler
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    bot.answer_callback_query(call.id)
    process_callback_query(call)


if __name__ == '__main__':
    logger.info("Bot is running :>")
    # keep_alive()
    try:
        bot.polling(non_stop=True)
    except BaseException:
        bot.polling(non_stop=True)
