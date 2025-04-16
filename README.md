# Address Bot

Basic Django application to run a bot to collect Ethereum addresses via Telegram

## Installation
Installation is recommended to be done in a virtual environment

```
virtualenv ab-env
source ab-env/bin/activate
```

Install requirements

```
pip install -r requirements.txt
```

By default it will store everything in a basic sqlite file

```
python manage.py makemigrations bot
python manage.py migrate
```

## Tests

Verify the environment is working and simulate a call to the bot:

```
pytest
```

Viewing the test configuration highlights what a call to the bot looks like.

## Run

Can spin up a basic Django server to load the bot. 

```
python manage.py runserver
```

If it is listening successfully, you can visit the webhook endpoint at http://127.0.0.1:8000/bot/webhook and it will echo back "4"

Of course, you'll need to set up an actual webserver to get the bot visible to the outside world in a production environment

Once you have a live webserver, set up your bot on Telegram [@BotFather](https://t.me/BotFather) and point to this endpoint.  Good luck!
