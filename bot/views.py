import json, os
import re
import uuid
import requests
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from bot.models import Update, User
from bot.telegram import (  # telegram_post,; delete_msg,; get_channel_name,; get_channel_type,; get_admin_chat_target,; update_msg,; update_msg_media,; update_msg_caption,; forward_message,; show_draft,; get_chat_admins,; is_user_admin,
    get_message_key,
    get_message_thread_id,
    run_post,
)
from bot.text import welcome_text
from bot.token import resolve_ens, gatekeep


gchat = settings.CHANNEL_DEBUG_LEVEL

@csrf_exempt
def webhook(request):
    # If the webhook returns an error code, the bot can go into an infinite loop.
    # PANIC! Panic! QUICK!  Quick!  Uncomment this line to break the issue:
    #return HttpResponse("4", content_type='text/plain')

    try:
        data = json.loads(request.body)
    except Exception as e:
        Update(raw=request.body, from_username="JSON ERROR").save()
        return HttpResponse("4", content_type="text/plain")

    from_username = None
    from_id = None
    try:
        message_key = get_message_key(data)

        if message_key == "callback_query":
            Update(
                raw=json.dumps(data),
                from_username="callback",
                text=data[message_key]["data"],
            ).save()

        else:
            from_id, from_username = fetch_username(data[message_key])
            if "text" in data[message_key]:
                data_text = data[message_key]["text"]
            elif "caption" in data[message_key]:
                data_text = data[message_key]["caption"]
            else:
                data_text = None
                text = None
            Update(
                telegram_id=data["update_id"],
                message_id=data[message_key]["message_id"],
                chat_id=data[message_key]["chat"]["id"],
                timestamp=data[message_key]["date"],
                from_id=from_id,
                from_username=from_username,
                raw=json.dumps(data),
                text=data_text,
            ).save()
    except Exception as e:
        Update(raw=json.dumps(data), from_username="DECODE ERROR", text=f"{e}").save()
        return HttpResponse("2", content_type="text/plain")

    try:
        if message_key == "message" and "new_chat_members" in data[message_key]:
            process_new_member(data, message_key, from_username, from_id)
    except Exception as e:
        run_post(f"Error kicking {e}", gchat)
        return HttpResponse("8", content_type="text/plain")

    # Callback queries are queries that post a specific command from a keyboard button
    if "callback_query" in data:
        return HttpResponse("4", content_type="text/plain")

    # Handle direct commands sent to the bot
    cmd = None
    if data[message_key].get("entities", None) or data[message_key].get(
        "caption_entities", None
    ):
        entities = data[message_key].get(
            "entities", data[message_key].get("caption_entities")
        )
        bot_offset = get_bot_offset(entities)
        if bot_offset is not None:
            if "text" in data[message_key]:
                text_data = data[message_key]["text"]
            elif "caption" in data[message_key]:
                text_data = data[message_key]["caption"]
            else:
                text_data = None

            if text_data:
                cmd = extract(text_data, entities[bot_offset])
                argument = extract_argument(text_data, cmd)
                chat_id = data[message_key]["chat"]["id"]
                message_thread = get_message_thread_id(data[message_key])
                cmd_orig = cmd
                cmd = f"{cmd}".lower()

    if cmd is None:
        return HttpResponse("1", content_type="text/plain")
    if "sign" in cmd:
        try:
            submit_eth_address(request)
        except Exception as e:
            run_post(f"Sign Bug {e}", gchat)

    if "ethereum" in cmd or "confirm" in cmd:
        try:
            if data[get_message_key(data)].get("chat").get("type") != "private":
                run_post(
                    f"You must run this command in private chat\nTry messaging: @{settings.TELEGRAM_BOT_USERNAME}",
                    chat_id,
                )
                return HttpResponse("6", content_type="text/plain")

            ethereum_address_regex = r"0x[a-fA-F0-9]{40}"
            match = re.search(ethereum_address_regex, argument)
            telegram = data[get_message_key(data)]["from"]["username"]
            try:
                telegram_id = data[get_message_key(data)]["from"]["id"]
            except:
                telegram_id = -1

            eth_address = None
            if match:
                eth_address = match.group()
            elif ".eth" in argument:
                try:
                    eth_address = resolve_ens(argument) 
                    if not eth_address:
                        raise ValueError("Invalid ENS name")
                except Exception as e:
                    run_post(
                        f"Error resolving ENS name: {str(e)}", chat_id, message_thread
                    )
                    return

            if eth_address:
                with transaction.atomic():
                    user, created = User.objects.get_or_create(
                        telegram_account=telegram,
                        username=f"tg:{telegram}-{telegram_id}",
                    )
                    user.ethereum_address = eth_address
                    user.save()

                try:
                    can_join, eligibility = gatekeep(eth_address)
                except Exception as e:
                    run_post(f"Error checking {eth_address} {telegram} {e}", gchat)
                    
                if can_join:
                    proceed_message = f"✅ Verified! {eligibility}\n🧺Access granted: <a href='{settings.TELEGRAM_GROUP_LINK}'>Join Chat</a>"
                    #proceed_message = f"Congrats!  You are invited to join our secret token-gated chat: <a href='{settings.TELEGRAM_GROUP_LINK}'>{settings.TELEGRAM_GROUP_LINK}</a>.\n\nYour wallet has been permitted to join this chat because you hold {eligibility}."
                else:
                    proceed_message = f"❌ Not Eligible: {eligibility}"
                    #proceed_message = f"Your address has been recorded, but unfortunately your wallet is not eligible to join our secret token-gated chat.\n\n{eligibility}"

                run_post(
                    f"📬 Address saved for username {telegram}: <code>{eth_address}</code>\n{proceed_message}",
                    chat_id,
                    message_thread,
                )
            else:
                check_existing = User.objects.filter(telegram_account=telegram).first()
                if check_existing:
                    run_post(
                            f"Address for username {telegram} is <code>{check_existing.ethereum_address}</code>\n\nTo change addresses, simply rerun this command with a different address: <code>/ethereum 0xNewAddress</code>",
                        chat_id,
                        message_thread,
                    )
                else:
                    if "confirm" in cmd:
                        text_arg = "confirm"
                    else:
                        text_arg = "ethereum"
                    run_post(eth_text(text_arg), chat_id, message_thread)

        except Exception as e:
            run_post(f"Error {e}", chat_id, message_thread)
    if "welcome" in cmd:
        run_post(welcome_text(), chat_id, message_thread)
    if "help" in cmd or "start" in cmd:
        if "start" in cmd:
            try:
                if data[get_message_key(data)]["chat"]["type"] != "private":
                    return HttpResponse("1", content_type="text/plain")
            except:
                pass

        admin = False
        run_post(welcome_text(admin), chat_id, message_thread)
    return HttpResponse("1", content_type="text/plain")


def fetch_username(data):
    try:
        if "from" in data:
            from_id = data["from"]["id"]
            from_username = data["from"]["username"]
        else:
            from_id = -1
            from_username = "unknown"
        return from_id, from_username
    except:
        return -1, "unknown"


def get_bot_offset(arr):
    for i in range(len(arr)):
        if arr[i]["type"] == "bot_command":
            return i
    return None


@csrf_exempt
def submit_eth_address(request):
    try:
        data = json.loads(request.body)
    except Exception as e:
        run_post(f"Error decoding JSON: {str(e)}", gchat)
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    message_key = get_message_key(data)

    chat_id = data[message_key]["chat"]["id"]
    telegram_username = data[message_key].get("from", {}).get("username")
    telegram_id = data[message_key].get("from", {}).get("id")
    text = data[message_key].get("text")
    eth_address = None

    if text and "/sign" in text:
        text_parts = text.split()
        if len(text_parts) == 2:
            input_value = text_parts[1]
            try:
                import  web3 as Web3
                w3 = Web3(Web3.HTTPProvider(f'https://mainnet.infura.io/v3/{settings.INFURA_API_KEY}'))
                if ".eth" in input_value:  # Check if the input is an ENS name
                    eth_address = w3.ens.address(input_value)
                    if not eth_address:
                        raise ValueError("Invalid ENS name")
                else:
                    eth_address = w3.to_checksum_address(input_value)
            except Exception as e:
                run_post(f"Error processing address or ENS name: {str(e)}", chat_id)
                return JsonResponse(
                    {"error": "Invalid Ethereum address or ENS name"}, status=400
                )

    # Check token balance
    token_contract = w3.eth.contract(
        address="0x5f3b5DfEb7B28CDbD7FAba78963EE202a494e2A2", abi=ERC20_ABI
    )
    token_balance = token_contract.functions.balanceOf(eth_address).call()

    if token_balance == 0:
        chat_id = data[message_key]["chat"]["id"]
        run_post(
            f"You do not have any balance of veCRV.  Use another address, or lock some veCRV and try again.",
            chat_id,
        )
        return JsonResponse({"error": "Insufficient token balance"}, status=400)

    # Generate a unique token and signing URL
    unique_token = str(uuid.uuid4())
    signing_url = f"{settings.DOMAIN}/sign/{unique_token}"

    # Store the necessary information in the database
    user, created = User.objects.get_or_create(
        telegram_account=telegram_username,
        username=f"tg:{telegram_username}-{telegram_id}",
    )
    user.ethereum_address = eth_address
    user.message_to_sign = (
        f"Please sign this message to verify your Ethereum address: {eth_address}"
    )
    user.unique_token = unique_token
    user.save()

    # Send the signing URL to the user
    chat_id = data[message_key]["chat"]["id"]
    run_post(f"Please sign the message by visiting this URL: {signing_url}", chat_id)

    return JsonResponse(
        {"message": "Please sign the message using the provided URL"}, status=200
    )


def process_new_member(data, message_key, from_username, from_id):
    try:
         
        run_post(f"New Member {data} {message_key} {from_username} {from_id}", gchat)
    except Exception as e:
        run_post(f"Weird error {e}", gchat)

def extract_argument(text, cmd):
    text_split = text.split(cmd)
    return text_split[1][1:]


def extract(text, e):
    start = int(e["offset"])
    end = int(e["length"]) + start
    return text[start:end]
