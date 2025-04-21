# Address Bot
![Open Reserve banner_one index](https://github.com/user-attachments/assets/371f6b9b-fb5c-4c0b-aa83-ae881671380b)

A Django application that runs a Telegram bot to collect and verify Ethereum addresses. This bot enables users to link their Telegram accounts with their Ethereum wallets, verify wallet ownership, and join private groups based on token holdings.

## Features

- Link Telegram accounts to Ethereum addresses
- ENS name resolution
- Token balance verification (SQUILL tokens)
- Private group access control based on token holdings
- Airdrop eligibility checking
- Message signing verification

## Prerequisites

- Python 3.8+
- PostgreSQL (optional, SQLite works for development)
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Infura API Key for Ethereum node access

## Installation

1. Clone the repository:
```
git clone <repository-url>
cd addressbot
```

2. Create and activate a virtual environment:
```
python -m venv ab-env
source ab-env/bin/activate  # On Windows: ab-env\Scripts\activate
```

3. Install requirements:
```
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with the following variables:
```
DOMAIN=your-domain.com
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_BOT_USERNAME=your_bot_username
TELEGRAM_GROUP_LINK=https://t.me/your_group_link
CHANNEL_INFO_LEVEL=your_channel_id
CHANNEL_DEBUG_LEVEL=your_debug_channel_id
RPC=https://mainnet.infura.io/v3/your_infura_key
INFURA_API_KEY=your_infura_api_key
SECRET_KEY=your_django_secret_key
MODE=development  # Set to 'production' for production environments

# PostgreSQL settings (optional)
POSTGRE_DBNAME=db_name
POSTGRE_USER=db_user
POSTGRE_PASS=db_password
POSTGRE_HOST=localhost
POSTGRE_PORT=5432
```

5. Set up the database:
```
python manage.py makemigrations bot
python manage.py migrate
```

## Testing

Run the tests:
```
pytest
```

For tests that interact with Telegram (which may cause notifications):
```
pytest --run-noisy
```

## Local Development

Start the development server:
```
python manage.py runserver
```

Your webhook will be available at: http://127.0.0.1:8000/bot/webhook

## Production Deployment

1. Set `MODE=production` and `DEBUG=False` in your environment
2. Configure a proper web server (nginx, Apache) with WSGI/ASGI
3. Set up your domain with SSL
4. Configure the webhook URL for your Telegram bot:
   ```
   https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url=https://your-domain.com/bot/webhook
   ```

## Commands

The bot responds to the following commands:
- `/ethereum [address]` - Link an Ethereum address to your Telegram account
- `/confirm [address]` - Alternative command for address linking
- `/welcome` - Display welcome message
- `/help` or `/start` - Display help information

## Security Notes

- Never commit your `.env` file to version control
- Set `DEBUG=False` in production
- Use a strong, random `SECRET_KEY`
- Keep your Telegram bot token and Infura API key secure

## License

[License information]

