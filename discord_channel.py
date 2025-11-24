from discord_webhook import DiscordWebhook

def send_discord_message(webhook_url, embed_data):
    
    webhook = DiscordWebhook(url=webhook_url, content="Daily Flight Tracker")

    webhook.add_embed(embed_data)

    return webhook.execute()