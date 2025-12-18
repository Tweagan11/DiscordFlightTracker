import os
import json
from discord_channel import send_discord_message
from serp import get_flights
from dotenv import load_dotenv
from datetime import datetime, timezone
from discord_webhook import DiscordEmbed
load_dotenv()

CACHE_FILE = "flights.json" 
FRONTEND_URL = "http://localhost:8080"
WEBHOOK_URL = os.environ["DISCORD_WEBHOOK"]



def load_flights():
    with open(CACHE_FILE, "r") as f:
        return json.load(f)
    
def parse_duration(minutes):
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours}h {mins}m"

def format_datetime(dt_string):
    dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
    return dt.strftime("%b %d, %I:%M %p")

def get_price_status(flight_data):
    
    price_insights = flight_data.get('price_insights', {})
    lowest_price = price_insights.get('lowest_price', 0)
    price_level = price_insights.get('price_level', 'typical')
    typical_range = price_insights.get('typical_price_range', [0, 0])
    
    if price_level == 'low' or lowest_price < typical_range[0]:
        return "Below Average", 0x00ff00 
    elif price_level == 'high' or lowest_price > typical_range[1]:
        return "Above Average", 0xff0000
    else:
        return "Typical Price", 0x0099ff 


def create_flight_embed(flight_data, top_n=3, message=""):
    """Create a Discord embed with top N flights"""
    
    # Sort flights by price, then by duration
    
    delta_flights = [f for f in flight_data['other_flights'] if f['flights'][0]['airline'] == 'Delta']
    
    # print(delta_flights[0])
    
    sorted_flights = sorted(
        flight_data['other_flights'],
        key=lambda x: (x['price'], x['total_duration'])
    )[:top_n]
    
    sorted_flights += flight_data.get('best_flight', [])
    sorted_flights = sorted(
        sorted_flights,
        key=lambda x: (x['price'], x['total_duration'])
    )[:top_n]
    
    min_delta = min(delta_flights, key=lambda x: x['price'])
    sorted_flights += [min_delta]
    
    print(sorted_flights)
    # Get price status
    price_status, embed_color = get_price_status(flight_data)
    
    # Get route info
    airports = flight_data['airports'][0]
    departure_info = airports['departure'][0]
    arrival_info = airports['arrival'][0]
    
    # Create main embed
    embed = DiscordEmbed(
        title=f"✈️ Flights: {departure_info['city']} → {arrival_info['city']} for {message}",
        description=f"**Price Status:** {price_status}\n**Lowest Price:** ${flight_data['price_insights']['lowest_price']}\n**Typical Range:** ${flight_data['price_insights']['typical_price_range'][0]} - ${flight_data['price_insights']['typical_price_range'][1]}" if flight_data.get('price_insights') else "",
        color=embed_color
    )
    embed.set_timestamp(datetime.now(timezone.utc))
    
    # Add each flight as a field
    for idx, flight in enumerate(sorted_flights, 1):
        
        # Get flight segments info
        segments = flight['flights']
        first_segment = segments[0]
        last_segment = segments[-1]
        
        # Build airlines list (unique)
        airlines = list(set([seg['airline'] for seg in segments]))
        airline_str = ", ".join(airlines)
        
        # Format departure and arrival
        dep_time = format_datetime(first_segment['departure_airport']['time'])
        arr_time = format_datetime(last_segment['arrival_airport']['time'])
        
        # Build flight legs information with durations
        flight_legs = []
        for i, segment in enumerate(segments):
            leg_duration = parse_duration(segment['duration'])
            dep_airport = segment['departure_airport']['id']
            arr_airport = segment['arrival_airport']['id']
            flight_legs.append(f"  ✈️ {dep_airport} → {arr_airport}: {leg_duration}")
            
            # Add layover info after this segment if there is one
            if i < len(segments) - 1 and flight.get('layovers'):
                layover = flight['layovers'][i]
                layover_duration = parse_duration(layover['duration'])
                overnight = " 🌙" if layover.get('overnight') else ""
                flight_legs.append(f"     ⏱️ Layover: {layover_duration}{overnight}")
        
        flight_legs_str = "\n".join(flight_legs)
        
        # Get the booking link from Google Flights
        google_flights_url = flight_data['search_metadata'].get('google_flights_url', '')
        
        # Build the field value
        field_value = (
            f"**Price:** ${flight['price']}\n"
            f"**Total Duration:** {parse_duration(flight['total_duration'])}\n"
            f"**Airlines:** {airline_str}\n"
            f"**Departure:** {dep_time}\n"
            f"**Arrival:** {arr_time}\n"
            f"**Stops:** {len(flight.get('layovers', []))}\n\n"
            f"**Flight Route:**\n{flight_legs_str}\n\n"
            f"[View on Google Flights]({google_flights_url})"
        )
        
        embed.add_embed_field(
            name=f"💺 Option {idx}",
            value=field_value,
            inline=False
        )
    
    # Add footer
    embed.set_footer(text=f"Showing top {len(sorted_flights)} flights • Data from Google Flights")
    
    return embed
    

def main():
    get_flights(outbound_date="2026-03-07", outbound_times="0,23")  # refresh cache
    data = load_flights()
    embed = create_flight_embed(data, top_n=1, message="for March 7th Departures")
    # print(embed)
    resp = send_discord_message(WEBHOOK_URL, embed)
    print("Sent webhook, status:", resp.status_code)
    
    get_flights()
    data = load_flights()
    embed = create_flight_embed(data, top_n=1, message="for March 6th Evening Departures")
    # print(embed)
    resp = send_discord_message(WEBHOOK_URL, embed)
    print("Sent webhook, status:", resp.status_code)

if __name__ == "__main__":
    main()
