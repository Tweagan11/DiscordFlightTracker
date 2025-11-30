from discord_webhook import DiscordWebhook
from datetime import datetime
from zoneinfo import ZoneInfo

def send_discord_message(webhook_url, embed_data):
    
    tz = ZoneInfo("America/Denver")
    now = datetime.now(tz)

    message = now.strftime("Lowest Flights as of %b %-d, %-I %p")
    
    webhook = DiscordWebhook(url=webhook_url, content=message)

    webhook.add_embed(embed_data)

    return webhook.execute()