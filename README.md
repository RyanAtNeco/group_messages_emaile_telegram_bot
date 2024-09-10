# Telegram Bot for Sending Group Messages to Email

This project is a Telegram bot that listens to messages in a group and sends messages containing a specific hashtag (`#SU`) to an email address.

## Prerequisites

- Python 3.x installed on your system.
- A Telegram bot token created via [BotFather](https://t.me/BotFather).
- An email account with SMTP server details (e.g., Gmail).
- `python-dotenv` library for managing environment variables.

## Setup Instructions

### 1. Clone or Download the Repository

Clone this repository or download it to your local machine.

### 2. Install Required Python Packages

Run the following command to install the required packages:

```bash
pip install -r requirements.txt
```

### 3. Create a `.env` File

Create a `.env` file in the root directory of your project with the following contents:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
EMAIL_ADDRESS=your_email@example.com
EMAIL_PASSWORD=your_email_password
TO_EMAIL_ADDRESS=recipient_email@example.com
```

Replace the placeholder values with your actual credentials:

- **TELEGRAM_BOT_TOKEN**: Your Telegram bot token from BotFather.
- **SMTP_SERVER**: Your email provider's SMTP server (e.g., `smtp.gmail.com` for Gmail).
- **SMTP_PORT**: The SMTP port (usually `587` for TLS).
- **EMAIL_ADDRESS**: Your email address from which the messages will be sent.
- **EMAIL_PASSWORD**: The password for your email account (or app-specific password if 2FA is enabled).
- **TO_EMAIL_ADDRESS**: The recipient email address where messages will be sent.

### 4. Update Your Bot Settings

1. **Disable Bot Privacy Mode**:
   - Go to [BotFather](https://t.me/BotFather).
   - Send the command `/mybots` and select your bot.
   - Choose **Bot Settings** > **Group Privacy**.
   - Set **Group Privacy** to **Disabled**.

2. **Add the Bot to a Group**:
   - Add the bot to the Telegram group where you want it to listen to messages.

3. **Promote the Bot to Admin (if Necessary)**:
   - Open the group settings and promote the bot to an admin to ensure it has the necessary permissions to read messages.

### 5. Run the Script

Run the Python script:

```bash
python main.py
```

### 6. Test the Bot

Send messages in the group where the bot is added and check the console output to ensure the bot is receiving messages. If the message contains the hashtag `#Raasti`, it will be sent to the specified email address.

### Troubleshooting

- **Bot Not Reading Messages**: Make sure the bot's privacy mode is disabled and that it has the necessary permissions to read messages.
- **Environment Variables Not Loaded**: Ensure that the `.env` file is correctly formatted and located in the project's root directory.

### Additional Notes

- **Do Not Share Your `.env` File**: Ensure that the `.env` file is listed in `.gitignore` to prevent it from being pushed to any public repositories.
- **Security**: Use app-specific passwords if your email provider supports two-factor authentication.

## License
This project is licensed under the MIT License.
