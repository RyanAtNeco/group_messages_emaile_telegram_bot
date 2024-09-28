from telegram import Update, ChatMember
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    ChatMemberHandler,
    filters,
    CallbackContext
)
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
import json

load_dotenv()

bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))  # Convert port to integer, with default 587
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID'))  # Admin's Telegram user ID

# Data files
GROUPS_FILE = 'groups.json'
CONFIG_FILE = 'group_configs.json'

# Load groups_seen and group_configs from files
if os.path.exists(GROUPS_FILE):
    with open(GROUPS_FILE, 'r') as f:
        groups_seen = json.load(f)
else:
    groups_seen = {}  # {group_id: group_title}

if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as f:
        group_configs = json.load(f)
else:
    group_configs = {}  # {group_id: {'hashtag': ..., 'email_address': ...}}

def save_groups():
    with open(GROUPS_FILE, 'w') as f:
        json.dump(groups_seen, f)

def save_configs():
    with open(CONFIG_FILE, 'w') as f:
        json.dump(group_configs, f)

def send_email(subject, body, to_email_address):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email_address

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_email_address, msg.as_string())

async def message_handler(update: Update, context: CallbackContext):
    if not update.message or not update.message.text:
        return  # Ignore non-text messages

    message = update.message.text
    sender = update.message.from_user.username or update.message.from_user.first_name
    chat = update.effective_chat

    print(f"Received message from {sender} in chat {chat.id}: {message}")

    # Check if group has a configured hashtag and email address
    group_id = str(chat.id)
    if group_id in group_configs:
        config = group_configs[group_id]
        hashtag = config.get('hashtag')
        to_email_address = config.get('email_address')
        if hashtag and to_email_address:
            if hashtag.lower() in message.lower():
                subject = f"New message from {sender} in Telegram Group ({chat.title})"
                body = f"Sender: {sender}\n\nMessage: {message}"
                send_email(subject, body, to_email_address)

# New handler for chat member updates
async def chat_member_handler(update: Update, context: CallbackContext):
    result = update.my_chat_member  # ChatMemberUpdated object
    chat = update.effective_chat
    new_status = result.new_chat_member.status

    # Check if the bot was added to a group
    if new_status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR]:
        group_id = str(chat.id)
        group_title = chat.title
        if group_id not in groups_seen:
            groups_seen[group_id] = group_title
            save_groups()
            print(f"Bot added to group {group_title} (ID: {group_id})")
    # Check if the bot was removed from a group
    elif new_status in [ChatMember.KICKED, ChatMember.LEFT]:
        group_id = str(chat.id)
        if group_id in groups_seen:
            del groups_seen[group_id]
            save_groups()
            print(f"Bot removed from group (ID: {group_id})")

# Admin commands
async def list_groups(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    if groups_seen:
        response = "Groups the bot is in:\n"
        for group_id, group_title in groups_seen.items():
            response += f"ID: {group_id}, Title: {group_title}\n"
    else:
        response = "No groups found."
    await update.message.reply_text(response)

async def set_config(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    args = context.args
    if len(args) < 3:
        await update.message.reply_text("Usage: /set_config <group_id> <hashtag> <email_address>")
        return

    group_id = args[0]
    hashtag = args[1]
    email_address = args[2]

    if group_id not in groups_seen:
        await update.message.reply_text("Group ID not found in bot's group list.")
        return

    group_configs[group_id] = {
        'hashtag': hashtag,
        'email_address': email_address
    }
    save_configs()
    await update.message.reply_text(f"Configuration set for group ID {group_id}.")

async def start_command(update: Update, context: CallbackContext):
    """Send instructions when the /start command is issued."""
    user_id = update.effective_user.id
    if user_id != ADMIN_USER_ID:
        return  # Only respond to the admin

    instructions = (
        "Welcome to the Telegram Bot!\n\n"
        "You can use the following commands:\n"
        "/list_groups - List all groups the bot is in.\n"
        "/set_config <group_id> <hashtag> <email_address> - Set the hashtag and email for a group.\n\n"
        "Example:\n"
        "/set_config -1001234567890 #alert example@example.com"
    )
    await update.message.reply_text(instructions)

async def on_startup(application: Application):
    """Function to run when the bot starts."""
    instructions = (
        "The bot has started and is ready to use!\n\n"
        "You can use the following commands:\n"
        "/list_groups - List all groups the bot is in.\n"
        "/set_config <group_id> <hashtag> <email_address> - Set the hashtag and email for a group.\n\n"
        "Example:\n"
        "/set_config -1001234567890 #alert example@example.com"
    )
    try:
        await application.bot.send_message(chat_id=ADMIN_USER_ID, text=instructions)
        print("Startup instructions sent to the admin.")
    except Exception as e:
        print(f"Failed to send startup message to admin: {e}")

def main():
    application = Application.builder().token(bot_token).post_init(on_startup).build()

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    application.add_handler(CommandHandler('list_groups', list_groups))
    application.add_handler(CommandHandler('set_config', set_config))
    application.add_handler(CommandHandler('start', start_command))
    # Add ChatMemberHandler to handle bot being added to or removed from groups
    application.add_handler(ChatMemberHandler(chat_member_handler, ChatMemberHandler.MY_CHAT_MEMBER))

    application.run_polling()

if __name__ == '__main__':
    main()
