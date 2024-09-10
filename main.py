from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()

bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))  # Convert port to integer, with default 587
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
TO_EMAIL_ADDRESS = os.getenv('TO_EMAIL_ADDRESS')

def send_email(subject, body):
  msg = MIMEText(body)
  msg['Subject'] = subject
  msg['From'] = EMAIL_ADDRESS
  msg['To'] = TO_EMAIL_ADDRESS

  with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
    server.starttls()
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    server.sendmail(EMAIL_ADDRESS, TO_EMAIL_ADDRESS, msg.as_string())

async def message_handler(update: Update, context: CallbackContext):
  message = update.message.text
  sender = update.message.from_user.username or update.message.from_user.first_name

  print(f"Received message from {sender}: {message}")

  if "#Raasti" in message:
    subject = f"New message from {sender} in Telegram Group"
    body = f"Sender: {sender}\n\nMessage: {message}"

    send_email(subject, body)

def main():
  application = Application.builder().token(bot_token).build()

  application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

  application.run_polling()

if __name__ == '__main__':
  main()
