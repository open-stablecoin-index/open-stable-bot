import json
import mimetypes
import os
import urllib.parse
from datetime import timedelta

import requests
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from bot.models import Update


def telegram_post(endpoint, data):
    token = settings.TELEGRAM_TOKEN
    url = f"https://api.telegram.org/bot{token}/{endpoint}"
    ret = requests.post(url, data=data)
    return ret


def delete_msg(chat_id, msg_id):
    data = dict(chat_id=chat_id, message_id=msg_id)
    ret = telegram_post("deleteMessage", data)
    return ret


def forward_message(
    from_message_chat_id, message_id, to_chat_id, to_message_thread_id=None
):
    token = settings.TELEGRAM_TOKEN
    url = f"https://api.telegram.org/bot{token}/forwardMessage?chat_id={to_chat_id}&from_chat_id={from_message_chat_id}&message_id={message_id}"
    if to_message_thread_id is not None:
        url += f"&message_thread_id={to_message_thread_id}"
    data = requests.get(url).json()
    return data


def run_post(
    message,
    chat_id=settings.CHANNEL_INFO_LEVEL,
    message_thread_id=None,
    attach_to_news=None,
    attach_tag=None,
):
    if settings.QUIET_MODE:
        Update(raw=message, chat_id=chat_id, from_username="log").save()
        return
    token = settings.TELEGRAM_TOKEN

    quoted_message = urllib.parse.quote_plus(message)
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={quoted_message}&parse_mode=html&disable_web_page_preview=True"
    if message_thread_id is not None:
        url += f"&message_thread_id={message_thread_id}"
    data = requests.get(url).json()
    if attach_to_news is not None:
        try:
            attach_to_news.add_message_id(
                chat_id, data["result"]["message_id"], attach_tag
            )
            print(f"Attached to news {chat_id} {data['result']['message_id']}")
        except Exception as e:
            print(f"Did not attach {e}")
    return data


def update_msg(chat_id, msg_id, new_text):
    data = dict(
        chat_id=chat_id,
        message_id=msg_id,
        text=new_text,
        parse_mode="html",
        disable_web_page_preview=True,
    )
    ret = telegram_post("editMessageText", data)
    return ret


def update_msg_caption(chat_id, msg_id, new_text):
    data = dict(
        chat_id=chat_id,
        message_id=msg_id,
        caption=new_text,
        parse_mode="html",
        disable_web_page_preview=True,
    )
    ret = telegram_post("editMessageCaption", data)
    return ret


def update_msg_media(chat_id, msg_id, news_item):
    data = dict(
        chat_id=chat_id,
        message_id=msg_id,
        media=json.dumps(
            {
                "type": "photo",
                "media": news_item.media_file.file.name,
                "caption": news_item.final,
                "parse_mode": "html",
            }
        ),
    )

    files = get_file_object_for_telegram(news_item.media_file.file.name)
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/editMessageMedia"
    ret = requests.post(url, data=data, files=files)
    return ret


def get_channel_name(data):
    channel_type = get_channel_type(data)
    if channel_type == "private":
        try:
            username = f"{data['message']['chat']['username']}"
        except Exception as e:
            username = "unknown"

        try:
            if (
                "last_name" in data["message"]["chat"]
                and "first_name" in data["message"]["chat"]
            ):
                channel_name = f"@{username} ({data['message']['chat']['first_name']} {data['message']['chat']['last_name']})"
            elif "first_name" in data["message"]["chat"]:
                channel_name = f"@{username} ({data['message']['chat']['first_name']})"
            else:
                channel_name = f"@{username}"
        except:
            channel_name = f"Unknown DM {e}"

        return channel_name, username

    if channel_type == "channel":
        try:
            channel_name = f"{data['chat']['title']}"
            username = f"{data['chat']['username']}"
        except:
            channel_name = "Unknown Channel"
            username = "unknown"
        return channel_name, username

    if "chat" in data:
        try:
            channel_name = f"{data['chat']['title']}"
            username = f"{data['chat']['username']}"
        except:
            channel_name = "Unknown Chat"
            username = "unknown"
        return channel_name, username

    if "message" in data:
        try:
            if "username" in data["message"]["chat"]:
                username = f"{data['message']['chat']['username']}"
            else:
                username = None
            if username:
                channel_name = f"@{username} ({data['message']['chat']['title']})"
            else:
                channel_name = f"{data['message']['chat']['title']}"
        except Exception as e:
            channel_name = f"Unknown message {e}"
            username = "unknown"
        return channel_name, username

    return f"Unknown other", "unknown"


def get_channel_type(data):
    try:
        channel_type = data["message"]["chat"]["type"]
    except Exception as e:
        try:
            channel_type = data["chat"]["type"]
        except Exception as e2:
            channel_type = f"unknown {e} {e2}"
    return channel_type


def get_admin_chat_target(chat_id):
    if chat_id == settings.CHANNEL_DEBUG_LEVEL:
        target = settings.CHANNEL_DEBUG_LEVEL
        thread = None
    else:
        target = settings.ADMIN_CHAT_DEFAULT
        thread = settings.ADMIN_MESSAGE_THREAD_DEFAULT
    return target, thread


def get_telegram_chat_id(user):
    if user.telegram_chat_id is not None:
        return user.telegram_chat_id
    if user.telegram_account is None:
        return None
    last_update = (
        Update.objects.filter(
            from_username=user.telegram_account, chat_id__gt=0, raw__icontains="private"
        )
        .order_by("-id")
        .first()
    )
    if last_update is None:
        return None
    if last_update.chat_id is not None:
        chat_id = last_update.chat_id
        user.telegram_chat_id = chat_id
        user.save(update_fields=["telegram_chat_id"])
        return chat_id
    return None


def get_chat_admins(chat_id):
    token = settings.TELEGRAM_TOKEN
    url = f"https://api.telegram.org/bot{token}/getChatAdministrators?chat_id={chat_id}"
    data = requests.get(url).json()
    return data


def is_user_admin(user_id, admin_data):
    # run_post(f"Admin Data is {admin_data}", gchat)
    for entry in admin_data["result"]:
        if entry["user"]["id"] == user_id:
            return True
    return False


def get_message_thread_id(data):
    if "reply_to_message" in data:
        if "message_thread_id" in data["reply_to_message"]:
            return data["reply_to_message"]["message_thread_id"]
    return None


def get_message_key(data):
    data_keys = list(data.keys())
    if "callback_query" in data_keys:
        return "callback_query"
    elif "message" in data_keys:
        return "message"
    elif "edited_message" in data_keys:
        return "edited_message"
    elif "channel_post" in data_keys:
        return "channel_post"
    elif "edited_channel_post" in data_keys:
        return "edited_channel_post"

    return data_keys[-1]


def unkick_member(chat_id, user_id):
    token = settings.TELEGRAM_TOKEN
    url = f"https://api.telegram.org/bot{token}/unbanChatMember?chat_id={chat_id}&user_id={user_id}&only_if_banned=true"
    data = requests.get(url)
    try:
        if data.json()["ok"] == True:
            return True
    except Exception as e:
        return f"Got exception {e}"
    return data.json()


def kick_member(chat_id, user_id):
    token = settings.TELEGRAM_TOKEN
    url = f"https://api.telegram.org/bot{token}/kickChatMember?chat_id={chat_id}&user_id={user_id}"
    data = requests.get(url)
    try:
        if data.json()["ok"] == True:
            return True
    except Exception as e:
        return f"Got exception {e}"
    return data.json()


def unban_chat_member(chat_id, user_id):
    token = settings.TELEGRAM_TOKEN
    url = f"https://api.telegram.org/bot{token}/unbanChatMember?chat_id={chat_id}&user_id={user_id}"
    return requests.get(url)
