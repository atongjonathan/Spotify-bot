import random
from info import data, vs
from keyboards import start_markup


class IgFollowers:
    def __init__(self):
        self.score = 0
        self.question_number = 0
        self.questions = 0
        self.first = random.choice(data)
        self.data = data
        self.second = random.choice(data)
        self.keyboard = ""
        self.output = ""
        self.percentage = 0

    def ask_question(self, bot, chat_id, keyboard):
        self.second = random.choice(data)
        self.keyboard = keyboard
        self.first = self.second
        self.second = random.choice(data)
        bot.send_message(chat_id,
                         f"🅰: {self.first['name']}, a {self.first['description']} from {self.first['country']}{vs}\b🅱:"
                         f" {self.second['name']} a {self.second['description']} from {self.second['country']}"
                         ".\n Who has more followers?🤷‍♂️", reply_markup=keyboard)
        self.questions += 1
        bot.register_next_step_handler_by_chat_id(chat_id,
                                                  lambda msg: self.check_answer(bot, msg))

    def check_answer(self, bot, message):
        input_text = message.text.lower()
        if input_text == 'a':
            if self.first["follower_count"] >= self.second["follower_count"]:
                bot.send_message(message.chat.id, "✅Correct!")
                self.score += 1
            else:
                bot.send_message(message.chat.id, "Wrong.❌")
        elif input_text == 'b':
            if self.second["follower_count"] >= self.first["follower_count"]:
                bot.send_message(message.chat.id, "✅Correct!")
                self.score += 1
            else:
                bot.send_message(message.chat.id, "Wrong.❌")
        elif input_text == 'stop':
            try:
                self.percentage = self.score / (self.questions - 1)
            except ZeroDivisionError:
                bot.send_message(message.chat.id, "To Restart click /ig_followers_game", reply_markup=start_markup)
            if self.percentage > 0.8:
                self.output = "𝕰𝖝𝖖𝖚𝖎𝖘𝖎𝖙𝖊!!"
            elif self.percentage / self.questions > 0.5:
                self.output = "𝓖𝓸𝓸𝓭 𝓳𝓸𝓫"
            elif self.percentage < 0.5:
                self.output = "𝓝𝓸𝓸𝓫𝓲𝓮"
            user_first_name = message.from_user.first_name
            bot.send_message(message.chat.id,
                             f"Game ended 🔒\n{user_first_name}, your final score is {self.score}/{self.questions - 1}"
                             f"🔥\n{self.output}")
            bot.send_message(message.chat.id, "To Restart click /ig_followers_game", reply_markup=start_markup)
            questions = 0
            return questions

        else:
            bot.send_message(message.chat.id, "⚠Invalid input. Please enter 'A' or 'B'")
        self.ask_question(bot, message.chat.id, self.keyboard)
