import os
import json
from discord import send_discord_message
from serp import get_flights
from dotenv import load_dotenv
import math
load_dotenv()

CACHE_FILE = "flights.json" 
FRONTEND_URL = "http://localhost:8080"
WEBHOOK_URL = os.environ["DISCORD_WEBHOOK"]



def load_flights():
    with open(CACHE_FILE, "r") as f:
        return json.load(f)
    
    
def pick_top_flights(flights_json, top_n=3):
    if "best_flight" in flights_json:
        flights = [flights_json["best_flight"]]
        return flights
        
    else:
        flights = flights_json["other_flights"]

        # Sort by price ascending
        sorted_flights = sorted(flights, key=lambda f: f["price"])

        return sorted_flights[:top_n]
   
def compute_price_range(data):

    insights = data.get("price_insights", {})
    typical_range = insights.get("typical_price_range")
    if typical_range and len(typical_range) == 2:
        low, high = typical_range
        avg = (low + high) / 2.0
        return int(low), int(high), float(avg)
    
    prices = [f.get("price") for f in data.get("other_flights", []) if isinstance(f.get("price"), (int, float))]
    if prices:
        low = int(min(prices))
        high = int(max(prices))
        avg = sum(prices) / len(prices)
        return low, high, float(avg)
    return None, None, None 

def duration_to_str(duration_minutes):
    hours = duration_minutes // 60
    minutes = duration_minutes % 60
    return f"{hours}h {minutes}m"


def format_embed(low, high, avg, top3):
    description = ""
    
    if low is not None:
        description = f"**Typical price range:** ${low} — ${high}  •  **Avg:** ${math.floor(avg)}"
    else:
        description = "Price range not available"
        
    embed = {
        "title": "Cheapest Flight Deals Today",
        "description": "Here are the top 3 cheapest flights right now!",
        "color": 0x1E90FF,
        "fields": [],
        "footer": {
            "text": "Updated automatically every morning at 8 AM MT"
        }
    }

    for idx, item in enumerate(top3, start=1):
        price = item.get("price", "N/A")
        # flights is an array of legs — use first leg for origin and last leg for destination
        legs = item.get("flights", [])
        if legs:
            origin = legs[0]["departure_airport"].get("id", legs[0]["departure_airport"].get("name", ""))
            dest = legs[-1]["arrival_airport"].get("id", legs[-1]["arrival_airport"].get("name", ""))
            # start / end times (take first departure time and last arrival time if available)
            dep_time = legs[0]["departure_airport"].get("time", "")
            arr_time = legs[-1]["arrival_airport"].get("time", "")
        else:
            origin = item.get("origin", "N/A")
            dest = item.get("destination", "N/A")
            dep_time = arr_time = ""

        total_duration = item.get("total_duration") or sum(leg.get("duration", 0) for leg in legs)
        airline_logo = item.get("airline_logo")
        airline = None
        # try to pick airline from first leg where available
        if legs:
            airline = legs[0].get("airline") or item.get("airline")
        if not airline:
            airline = "Multiple airlines"

        # small summary for field value
        value_lines = [
            f"**Price:** ${price}",
            f"**Airline:** {airline}",
            f"**Route:** {origin} → {dest}",
            f"**Total duration:** {duration_to_str(total_duration)}"
        ]
        # include first layover info if present
        layovers = item.get("layovers") or []
        if layovers:
            # show number of stops and if overnight
            stops = len(layovers)
            overnight = any(lp.get("overnight") for lp in layovers)
            lo = f"{stops} stop{'s' if stops != 1 else ''}"
            if overnight:
                lo += " (overnight)"
            value_lines.append(f"**Stops:** {lo}")

        # include carbon emissions summary if present
        ce = item.get("carbon_emissions")
        if ce and isinstance(ce, dict):
            diff = ce.get("difference_percent")
            if diff is not None:
                # show simple emoji
                emo = "🔺" if diff > 10 else ("🔻" if diff < -10 else "⚖️")
                value_lines.append(f"**Emissions vs typical:** {diff}% {emo}")

        # include a short 'details' link — we point to frontend; you can expand to link to a per-flight page
        value_lines.append(f"[View more on site]({FRONTEND_URL})")

        field = {
            "name": f"{idx}. {airline} — {origin} → {dest}  —  ${price}",
            "value": "\n".join(value_lines),
            "inline": False
        }
        embed["fields"].append(field)

        # use the first airline logo as embed thumbnail (only set once)
        if airline_logo and "thumbnail" not in embed:
            embed["thumbnail"] = {"url": airline_logo}

    return embed
    

def main():
    get_flights()  # refresh cache
    data = load_flights()
    low, high, avg = compute_price_range(data)
    top3 = pick_top_flights(data, top_n=3)
    embed = format_embed(low, high, avg, top3)
    resp = send_discord_message(WEBHOOK_URL, embed)
    print("Sent webhook, status:", resp.status_code)

if __name__ == "__main__":
    main()