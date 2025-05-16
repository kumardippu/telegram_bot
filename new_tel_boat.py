import json
import os
import re
from datetime import datetime

from config import TELEGRAM_TOEKN
from pnr_lookup import fetch_pnr_details  # Import your PNR fetch function
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

CONTACT_FILE = "contacts.json"

# Load existing data or initialize
if os.path.exists(CONTACT_FILE):
    with open(CONTACT_FILE, "r") as f:
        user_data = json.load(f)
else:
    user_data = {}

def save_data():
    with open(CONTACT_FILE, "w") as f:
        json.dump(user_data, f, indent=2)

async def ask_for_pnr(update: Update):
    contact_button = KeyboardButton("Send PNR Number")
    reply_markup = ReplyKeyboardMarkup(
        [[contact_button]],
        one_time_keyboard=True,
        resize_keyboard=True
    )
    await update.message.reply_text(
        "Please enter your 10-digit PNR number:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    message = update.message.text if update.message else ""
    now = datetime.utcnow().isoformat()

    # Initialize user record if missing or invalid
    if user_id not in user_data or not isinstance(user_data[user_id], dict):
        user_data[user_id] = {}

    # If user shared contact
    if update.message and update.message.contact:
        phone_number = update.message.contact.phone_number
        user_data[user_id].update({
            "user_id": user_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "phone_number": phone_number,
            "last_message": "shared contact",
            "timestamp": now
        })
        save_data()
        await update.message.reply_text(f"Thanks! Got your number: {phone_number}")
        # Now ask for PNR
        await update.message.reply_text("Now, please send me your 10-digit PNR number.")
        return

    # If user has shared phone number before
    if user_data.get(user_id, {}).get("phone_number"):
        # Check if message looks like a PNR number (10 digits)
        if re.fullmatch(r"\d{10}", message.strip()):
            pnr = message.strip()
            user_data[user_id].update({
                "pnr": pnr,
                "last_message": f"PNR entered: {pnr}",
                "timestamp": now
            })
            save_data()

            # Fetch PNR details and send
            await update.message.reply_text("Fetching PNR details, please wait...")
            pnr_details = fetch_pnr_details(pnr)
            await update.message.reply_text(pnr_details)
        else:
            # For any other message, greet or ask for PNR
            await update.message.reply_text(
                f"Welcome back, {user.first_name}! I already have your number: {user_data[user_id]['phone_number']}\n"
                "Please send your 10-digit PNR number to check status."
            )
    else:
        # Ask for contact if message is "hello"
        if message.strip().lower() == "hello":
            contact_button = KeyboardButton("Share Contact ☎️", request_contact=True)
            reply_markup = ReplyKeyboardMarkup(
                [[contact_button]],
                one_time_keyboard=True,
                resize_keyboard=True
            )
            await update.message.reply_text(
                "Please share your contact number by tapping the button below:",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text("Say 'hello' to start! 😄")

    # Update latest message and timestamp without erasing phone number
    user_data[user_id].update({
        "user_id": user_id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "last_message": message,
        "timestamp": now
    })

    save_data()

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOEKN).build()
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()