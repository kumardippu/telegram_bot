TOKEN = '7838570978:AAEy0jrbqZAdhqw9eJ46bTWbvcez4tPf9D8'
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Replace with your actual token
#TOKEN = '*******'

# Keep track of who the bot is waiting on for a name
user_state = {}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message.text.strip().lower()

    # If the user said "hello"
    if message == "hello":
        user_state[user_id] = "awaiting_name"
        await update.message.reply_text("Hey there! What's your name?")
    
    # If we are waiting for this user's name
    elif user_state.get(user_id) == "awaiting_name":
        name = update.message.text.strip().title()
        await update.message.reply_text(f"Nice to meet you, {name}! 😊")
        user_state.pop(user_id)  # Reset the state

    else:
        await update.message.reply_text("Say 'hello' to start the fun! 😄")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
