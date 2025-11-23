# Discord Flight Tracker
This app will track flights for given destinations and update us via Discord at least daily.
SerpAPI to scrape Google flights on a limited basis (250/Month). This is a personal project for our personal discord.

To achieve this, we will query SerpAPI 1-2 times per day with multiple locations. This will store a JSON object that we can refer to and compare other flights. Once this is queried, we can parse through the given flights and send the best offers to our channel. Since this is a one way communication, we will just implement a webhook for now and possibly institute a bot later. 

# Features:
- Configure app for given date (span), Airport, and destination
- Post at least daily in discord app, possibly update if big drop in price
- Sort found flights by price, duration, and layovers.
- 

# Resources:
- SerpAPI [https://serpapi.com/]
- Discord API [https://discord.com/developers/docs/reference]
- Discord Webhook from PyPi [https://pypi.org/project/discord-webhook/]
