from discord_webhook import DiscordWebhook, DiscordEmbed

def send_discord_message(webhook_url, embed_data):
    # 1. Create webhook
    webhook = DiscordWebhook(url=webhook_url, content="Daily Flight Tracker")

    # 2. Create embed from your dict
    embed = DiscordEmbed(
        title=embed_data["title"],
        description=embed_data["description"],
        color=embed_data["color"]
    )

    # Add fields
    for field in embed_data.get("fields", []):
        embed.add_embed_field(
            name=field["name"],
            value=field["value"],
            inline=field["inline"]
        )

    # Add thumbnail if present
    if "thumbnail" in embed_data:
        embed.set_thumbnail(url=embed_data["thumbnail"]["url"])

    # Add footer
    if "footer" in embed_data:
        embed.set_footer(text=embed_data["footer"]["text"])

    # Add timestamp
    if "timestamp" in embed_data:
        embed.set_timestamp(embed_data["timestamp"])

    # 3. Attach embed to webhook
    webhook.add_embed(embed)

    # 4. Send
    return webhook.execute()