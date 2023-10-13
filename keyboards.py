from telebot import types
import random
import html
class Keyboard():
    def __init__(self) -> None:
        self.views_keyboard = types.InlineKeyboardMarkup()
        self.lyrics_keyboard = types.InlineKeyboardMarkup()
        self.list_of_keyboard = types.InlineKeyboardMarkup()
        self.hide_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
        self.hide_button = types.KeyboardButton("⬆️ Show command buttons")
        self.hide_keyboard.add(self.hide_button)


        self.force_markup = types.ForceReply()
        self.start_markup = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                one_time_keyboard=False)
        self.start_markup.row("⬇️ Hide command buttons")
        self.start_markup.row('/song', '/artist')
        self.start_markup.row('/lyrics', '/ping')

    def make_for_type (self,artist_id, type, list_of_type):
        for album in list_of_type:
            album_name = album["name"]
            small_id = artist_id.split(':')[2]
            small_uri = album['uri'].split(':')[2]
            data = f"{small_id}_{type}_{small_uri}"
            button = types.InlineKeyboardButton(album_name, callback_data=data)
            self.list_of_keyboard.add(button)
        close = types.InlineKeyboardButton("Close", callback_data='close_make')
        self.list_of_keyboard.add(close)
        return self.list_of_keyboard


    def lyrics_handler(self,artist,title):
        lyrics_button = types.InlineKeyboardButton(text="Get Lyrics", callback_data=f"lyrics_{title}_{artist}")
        self.lyrics_keyboard.add(lyrics_button)
        return self.lyrics_keyboard


    def view_handler(self,name):
        self.views_keyboard = types.InlineKeyboardMarkup()
        top_tracks_button = types.InlineKeyboardButton(f"{name}'s Top Tracks🔝",callback_data=f"toptracks_{name}")
        self.views_keyboard.add(top_tracks_button)
        # if len(list_of_albums)>0:
        #     data = f'album_{artist_uri}'
        #     album_list_button = types.InlineKeyboardButton(f"View {name}'s Albums🧐", callback_data=data)
        #     self.views_keyboard.add(album_list_button)
        # if len(list_of_singles)>0:
        #     data = f'single_{artist_uri}'
        #     single_list_button = types.InlineKeyboardButton(f"View {name}'s Singles or EPs🧐", callback_data=data)
        #     self.views_keyboard.add(single_list_button)
        return self.views_keyboard

        
    # def create_keyboard(all_answers):
    #     answers_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    #     random.shuffle(all_answers)
    #     for answer in all_answers:
    #         button = types.KeyboardButton(html.unescape(answer))
    #         answers_keyboard.add(button)
    #     close = types.InlineKeyboardButton("Close", callback_data='close_handler')
    #     answers_keyboard.add(close)
    #     return answers_keyboard


