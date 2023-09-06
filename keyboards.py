from telebot import types
import random
import html


def make_for_type (artist_id, type, list_of_type):
    answers_keyboard = types.InlineKeyboardMarkup()
    for album in list_of_type:
        album_name = album["name"]
        small_id = artist_id.split(':')[2]
        small_uri = album['uri'].split(':')[2]
        data = f"{small_id}_{type}_{small_uri}"
        button = types.InlineKeyboardButton(album_name, callback_data=data)
        answers_keyboard.add(button)
    return answers_keyboard
def lyrics_handler(artist,title):
    handler_markup = types.InlineKeyboardMarkup()
    lyrics_button = types.InlineKeyboardButton(text="Get Lyrics", callback_data=f"lyrics_{title}_{artist}")
    handler_markup.add(lyrics_button)
    return handler_markup

def handler(name,artist_uri, list_of_albums,list_of_singles):
    markup = types.InlineKeyboardMarkup()
    top_tracks_button = types.InlineKeyboardButton(f"{name}'s Top Tracks🔝",callback_data=f"track_{artist_uri}")
    markup.add(top_tracks_button)
    if len(list_of_albums)>0:
        data = f'album_{artist_uri}'
        album_list_button = types.InlineKeyboardButton(f"View {name}'s Albums🧐", callback_data=data)
        markup.add(album_list_button)
    if len(list_of_singles)>0:
        data = f'single_{artist_uri}'
        single_list_button = types.InlineKeyboardButton(f"View {name}'s Singles or EPs🧐", callback_data=data)
        markup.add(single_list_button)    
    return markup
def create_keyboard(all_answers):
    answers_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    random.shuffle(all_answers)
    for answer in all_answers:
        button = types.KeyboardButton(html.unescape(answer))
        answers_keyboard.add(button)
    return answers_keyboard

hide_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
hide_button = types.KeyboardButton("⬆️ Show command buttons")
hide_keyboard.add(hide_button)

difficulty_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
easy = types.KeyboardButton("Easy")
medium = types.KeyboardButton("Medium")
hard = types.KeyboardButton("Hard")
difficulty_keyboard.add(easy, medium, hard)


yes_no_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
yes = types.KeyboardButton("Yes")
no = types.KeyboardButton("No")
yes_no_keyboard.add(yes,no)


force_markup = types.ForceReply()
start_markup = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                         one_time_keyboard=False)
start_markup.row("⬇️ Hide command buttons")
start_markup.row('/lyrics', '/song', '/artist')
start_markup.row('/quote', '/status')

keyboard = types.ReplyKeyboardMarkup(
    row_width=2,
    resize_keyboard=True,
)
button_A = types.KeyboardButton("A")
button_B = types.KeyboardButton("B")
button_C = types.KeyboardButton("Stop")
keyboard.row(button_A, button_B)
keyboard.row(button_C)

sport = types.ReplyKeyboardMarkup(
    row_width=2,
    resize_keyboard=True,
)
handball = types.KeyboardButton("Handball")
tennis = types.KeyboardButton("Tennis")
basketball = types.KeyboardButton("Basketball")
football = types.KeyboardButton("Football")
sport.row(football, basketball)
sport.row(tennis, handball)

trivia_keyboard = types.ReplyKeyboardMarkup(
    row_width=2,
    resize_keyboard=True,
)
button_true = types.KeyboardButton("True")
button_false = types.KeyboardButton("False")
stop_button = types.KeyboardButton("Stop")
trivia_keyboard.row(button_true, button_false)
trivia_keyboard.row(stop_button)

category_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                              row_width=3)
anime_button = types.KeyboardButton("Anime & Manga")
science_button = types.KeyboardButton("Science and Nature")
history_button = types.KeyboardButton("History")
general_button = types.KeyboardButton("General Knowledge")
computers_button = types.KeyboardButton("Computers")
music_button = types.KeyboardButton("Music")
politics_button = types.KeyboardButton("Politics")
sports_button = types.KeyboardButton("Sports")
celebrities_button = types.KeyboardButton("Celebrities")
category_keyboard.row(anime_button, science_button, history_button)
category_keyboard.row(general_button, music_button, computers_button)
category_keyboard.row(politics_button, sports_button, celebrities_button)
