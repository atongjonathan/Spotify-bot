import telebot

# Your Telegram Bot Token
TELEGRAM_BOT_TOKEN = "6453092959:AAH65NtLGOXgR3F6Ak30FXCN1tguOnxQpZA"
bot =telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Define bot handlers
@bot.message_handler(commands=["start"])
def handle_start(message):
    bot.reply_to(message, "Hello! This is your bot.")

@bot.message_handler(commands=["senddocument"])
def send_document(message):
    # Replace 'path_to_document.pdf' with the actual path to your document file
    document_path = "perc.mp4"
    try:
        with open(document_path, 'rb') as document_file:
            bot.send_video(message.chat.id, document_file, supports_streaming=True)
    except Exception as e:
        print(e)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)

print("Running")
bot.polling()
