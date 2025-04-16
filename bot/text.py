from django.conf import settings


def guest_text():
    return "Thank you for joining the Leviathan News Livestream!\n\
\n\
Livestreams occur every weekday at 2:00 PM UTC (7 AM PT, 10 AM ET).  They usually run for 20 minutes, during which we provide running commentary about the last 24 hours of crypto news.  When a guest participates, we usually offer the guest 10 minutes of Q&A on their topic, after which they can leave or join us to chat about news.\n\
\n\
Scheduling is handled through our Calendly (which has only 15 minute slots because we don't want to pay Calendly): https://calendly.com/lnnheadlines/interview\n\
\n\
When joining, set your username to `@your_twitter_handle` if you use Twitter so people can more easily find you.  Also inform the hosts of any topics you prefer we do not discuss before we go live.\n\
\n\
We will send you a link to join the stream when it is ready\n\
\n\
To see past episodes, please check our prior streams at YouTube (https://www.youtube.com/@Leviathan_News) or Spotify (https://open.spotify.com/show/69yxNKomUIbdNMFoTjp49K)\n\
\n\
Make sure to run the /ethereum command in a direct DM with the bot (@{settings.TELEGRAM_BOT_USERNAME}) for a good time!\n\
\n\
If you have other questions, please inquire in the Telegram channel: https://t.me/+zqRS5HW8GlgzY2Ix"


def eth_text(cmd="ethereum"):
    return f"<b><u>Link ETH Address</u></b>\n\
\n\
The bot can help you confirm your ETH address has been linked to your Telegram account.  The bot handles no private keys.\n\
\n\
<code>/{cmd} [YOUR ETH ADDRESS]</code>\n\
\n\
You can confirm if your ETH address was linked by just typing this command without any arguments\n\
\n\
<code>/{cmd}</code>\n\
"


def noisy_text(channel_name):
    return f"Leviathan News Bot now posting alerts in Telegram Channel: {channel_name} \nType /noisy to suppress or type /help to see a list of commands"


def noisy_cancel_text(channel_name):
    return f"Leviathan News Bot no longer posting alerts in Telegram Channel: {channel_name}\nType /noisy to re-enable or type /help to see a list of commands"


def noisy_admin_text(channel_name=None):
    return f"Only channel admins can adjust Leviathan Bot channel settings"


def welcome_text(admin=False):
    main_text = "<b>Welcome to the Open Dollar bot!</b>\n\
\n\
Although we want to make the dollar open, our chat is closed.  In order to join this private group, you must verify your Ethereum address.  Type <code>/ethereum 0xYOUR_ADDR</code> with an address that has SQUILL to start the process.\n\
\n\
<b>Available Commands</b>\n\
• /help This Message\n\
• /ethereum Confirm your address"
    
    return main_text


def regulate_private_text():
    return f"This command is only available in private chat, try DM-ing @{settings.TELEGRAM_BOT_USERNAME}"


def regulate_success():
    return f"⚖️ Success!  You are now a regulator! 🤝\n\
\n\
As news gets posted, you will see a panel slide into your DMs with various regulatory options.  Click buttons, earn points!\n\
\n\
If you have questions, please inquire within the Squid Cave: https://t.me/+KWxvHCpN6ANhYWVi"


def regulate_disable():
    return f"👋 Farewell citizen, you will no longer receive alerts with new news, and you will no longer earn points.\n\
\n\
If you'd like to rejoin the regulators, type /regulate to resume your duties."


def points_help():
    return "\n\nWant more detail?  Try the following commands:\n\
 • <code>/points 5</code> : Point breakdown for the month of May, also accepts <code>/points May</code> or similar \n\
 • <code>/points 5817</code> : Point breakdown for article id 5817"
