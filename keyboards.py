from telebot import types


class Keyboard():
    def __init__(self) -> None:
        self.hide_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        self.hide_button = types.KeyboardButton("⬆️ Show command buttons")
        self.hide_keyboard.add(self.hide_button)

        self.force_markup = types.ForceReply()

        self.start_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        self.start_markup.row("⬇️ Hide command buttons")
        self.start_markup.row('/artist', '/song')
        self.start_markup.row('/commands', '/ping')

    def _make_sub_lists(self, list_of_type, items_per_page):
        items_per_page = 5
        lists = []

        for i in range(0, len(list_of_type), items_per_page):
            sublist = list_of_type[i:i + items_per_page]
            lists.append(sublist)
        return lists

    def keyboard_for_results(self, results):
        keyboard = types.InlineKeyboardMarkup(row_width=4)
        close = types.InlineKeyboardButton(
            "Close", callback_data=f'close_make')
        for idx, result in enumerate(results):
            button = types.InlineKeyboardButton(
                str(idx + 1), callback_data=f"r_{result['uri']}")
            keyboard.row(button)
        keyboard.row(close)
        return keyboard

    def make_for_type(self, list_of_type, current_page):
        try:
            for key, value in list_of_type.items():
                list_of_type = value
                one_type = key
        except Exception as e:
            one_type = "toptracks"
            pass
        pages_list = self._make_sub_lists(list_of_type, 5)
        keyboard = types.InlineKeyboardMarkup()
        if len(list_of_type) == 0:
            pass
        else:
            page = pages_list[current_page]
            for album in page:
                name = album["name"]
                uri = album["uri"]
                artist_uri = album["artist_uri"]
                button = types.InlineKeyboardButton(
                    f"{name}", callback_data=uri)
                keyboard.add(button)
        next = types.InlineKeyboardButton(
            "Next >>", callback_data=f'_n_{artist_uri}_{one_type}_{current_page}')
        previous = types.InlineKeyboardButton(
            "<< Previous", callback_data=f'_p_{artist_uri}_{one_type}_{current_page}')
        close = types.InlineKeyboardButton(
            "Close", callback_data=f'close_make')
        number_of_pages = len(pages_list) - 1
        if not current_page == number_of_pages and current_page < number_of_pages:
            keyboard.add(next)
        if current_page > 0:
            keyboard.add(previous)
        keyboard.add(close)
        return keyboard

    def lyrics_handler(self, artists, uri):
        keyboard = types.InlineKeyboardMarkup()
        lyrics_button = types.InlineKeyboardButton(
            text=f'Get "{artists}" lyrics', callback_data=f'lyrics_{uri}')
        keyboard.add(lyrics_button)
        return keyboard

    def view_handler(self, name, uri, lengths):
        keyboard = types.InlineKeyboardMarkup()
        top_tracks_button = types.InlineKeyboardButton(
            f"Top Tracks🔝", callback_data=f"toptracks_{uri}")
        keyboard.add(top_tracks_button)
        type = ['single', 'album', 'compilation']
        for idx, item in enumerate(lengths):
            if (item > 0):
                button = types.InlineKeyboardButton(
                    f"View {name}'s {type[idx].title()}s🧐", callback_data=f"{type[idx]}_{uri}")
                keyboard.row(button)
        return keyboard


keyboard = Keyboard()
