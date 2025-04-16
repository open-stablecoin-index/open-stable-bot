from django.conf import settings
import requests
import urllib.parse


def get_channel_info(channel_id):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/getChat?chat_id={channel_id}"
    data = requests.get(url).json()
    print(data)
    return data


def get_webhook():
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/getWebhookInfo"
    print(f"Fetching webhook for {url}")
    data = requests.get(url).json()
    print(f"Got: {data}")
    return data


def set_webhook(webhook_url):
    parsed_webhook = urllib.parse.quote_plus(webhook_url)
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/setWebhook?url={parsed_webhook}"

    data = requests.get(url).json()
    print(data)
    return data
