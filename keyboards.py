from telebot import types


class Keyboard():
    def __init__(self) -> None:
        self.hide_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        self.hide_button = types.KeyboardButton("⬆️ Show command buttons")
        self.hide_keyboard.add(self.hide_button)

        self.force_markup = types.ForceReply()

        self.start_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        self.start_markup.row("⬇️ Hide command buttons")
        self.start_markup.row('/song', '/artist')
        self.start_markup.row('/commands', '/ping')

    def make_for_type(self, list_of_type):
        keyboard = types.InlineKeyboardMarkup()
        if len(list_of_type) == 0:
            pass
        else:
            for idx, album in enumerate(list_of_type):
                name = album["name"]
                uri = album["uri"]
                button = types.InlineKeyboardButton(
                    f"{idx+1}. {name}", callback_data=uri)
                keyboard.add(button)
            close = types.InlineKeyboardButton(
                "Close", callback_data=f'close_make')
            keyboard.add(close)
        return keyboard

    def lyrics_handler(self, artists, uri):
        keyboard = types.InlineKeyboardMarkup()
        lyrics_button = types.InlineKeyboardButton(
            text=f"Get {artists} Lyrics", callback_data=f"lyrics_{uri}")
        keyboard.add(lyrics_button)
        return keyboard

    def view_handler(self, name):
        keyboard = types.InlineKeyboardMarkup()
        top_tracks_button = types.InlineKeyboardButton(
            f"Top Tracks🔝", callback_data=f"toptracks_{name}")
        singles_button = types.InlineKeyboardButton(
            f"Singles or EPs🧐", callback_data=f"single_{name}")
        albums_tracks_button = types.InlineKeyboardButton(
            f"Albums 🧐", callback_data=f"album_{name}")
        compilation_button = types.InlineKeyboardButton(
            f"Compilations 🧐", callback_data=f"compilation_{name}")
        keyboard.row(top_tracks_button, singles_button)
        keyboard.row(albums_tracks_button, compilation_button)
        return keyboard
