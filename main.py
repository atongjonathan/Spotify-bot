import time
import warnings
from logging import FileHandler, StreamHandler, INFO, basicConfig, getLogger
from utils import keyboard, bot, search_artist, search_song, process_callback_query
import billboard
from spotify import Spotify


basicConfig(
    format='SG-Bot | %(levelname)s | %(asctime)s - %(name)s - line %(lineno)d | %(message)s',
    handlers=[FileHandler('logs.txt'),
              StreamHandler()],
    level=INFO)
logger = getLogger(__name__)

# Filter out specific warnings from spotipy.cache_handler
warnings.filterwarnings("ignore")

def reply_to_query(message,reply_text,search_function):
    bot.reply_to(message,reply_text,reply_markup=keyboard.force_markup)
    bot.register_next_step_handler_by_chat_id(message.chat.id,
                                            lambda msg: search_function(msg))    

def get_search_query(message, command, function, reply_text):
    text = message.text    
    if " " in text:
        query = text.replace(f"/{command} ", "")
        function(message, query)
    else:
        reply_to_query(message, reply_text, function)

def search_trending(message, no_of_songs):
    reply = bot.send_message(message.chat.id, "Awesome getting trending somgs in a few")
    hot_100 = billboard.ChartData("hot-100")[:no_of_songs]
    spotify = Spotify()
    track_details = [spotify.song(artist=item.artist,title=item.title)[0] for item in hot_100]
    result_string = [f'{idx+1}. `{item["name"]}` - {item["artists"]}' for idx, item in enumerate(track_details)]
    result_string = '\n'.join(result_string)
    artists_keyboard = keyboard.keyboard_for_results(results=track_details)
    bot.delete_message(reply.chat.id, reply.id)
    bot.send_message(
        message.chat.id,
        f"Trending Songs\n\n{result_string}",
        reply_markup=artists_keyboard)

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
    artist_reply = "Send me the name of the artist"
    get_search_query(message, "artist", search_artist, artist_reply)


@bot.message_handler(commands=["song"])
def get_song(message):
    song_reply = "Send me the song title followed by the artist separated by a comma for optimal results"
    get_search_query(message, "song", search_song, song_reply)


@bot.message_handler(commands=['trending'])
def trending(message):
    text = message.text
    if " " not in text:
        no_of_songs = 10
    else:
        no_of_songs = int(text.replace(f"/trending ", ""))        
        if no_of_songs > 100:
            bot.reply_to(message, "Number requested to should be less than 100")
            return
    search_trending(message, no_of_songs=no_of_songs)



@bot.message_handler(commands=['commands'])
def info(message):
    bot.reply_to(
        message,
        "/start - Starts the bot\n/song - Search for a song\n/artist - Search for an artist\n/ping - Test Me"
    )




@bot.message_handler(commands=['logs'])
def get_logs(message):
    with open("logs.txt") as file:
        bot.send_document(message.chat.id, file,
                        reply_markup=keyboard.start_markup)


@bot.message_handler(commands=['ping'])
def ping(message):
    start_time = time.time()
    response = bot.reply_to(message, "Pinging...")
    end_time = time.time()
    elapsed_time_ms = int((end_time - start_time) * 1000)

    bot.edit_message_text(f"Pong! 🏓\nResponse Time: `{elapsed_time_ms} ms`",
                          chat_id=message.chat.id,
                          message_id=response.message_id)


@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text == "⬆️ Show command buttons":
        bot.reply_to(message,
                         "⬆️ Show command buttons",
                         reply_markup=keyboard.start_markup)
    elif message.text == "⬇️ Hide command buttons":
        bot.reply_to(message,
                         "⬇️ Hide command buttons",
                         reply_markup=keyboard.hide_keyboard)


# Set up a callback query handler
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    process_callback_query(call)


if __name__ == '__main__':
    logger.info("Bot is running :>")
    try:
        bot.polling(non_stop=True)
    except BaseException:
        bot.polling(non_stop=True)
