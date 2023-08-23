from telebot import types
import random
import html


def create_album_keyboard (list_of_albums):
    answers_keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
    for album in list_of_albums:
        button = types.InlineKeyboardButton(album["name"]) 
        answers_keyboard.add(button)
    return answers_keyboard
def get_handler_of_artist(name,uri,list_of_albums):
    handler_markup = types.InlineKeyboardMarkup()
    top_tracks_button = types.InlineKeyboardButton(f"{name.title()}'s Top Tracks🔝",callback_data=f"track_{uri}")
    if len(list_of_albums)>0:
        album_list_button = types.InlineKeyboardButton("View Album🧐", callback_data=f'album_{uri}')
        handler_markup.row(top_tracks_button,album_list_button)
    else:
        handler_markup.row(top_tracks_button)
    return handler_markup
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
start_markup.row('/song', '/artist', '/topsongs')
start_markup.row('/quote', '/status', '/info')

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
