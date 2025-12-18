from serpapi import GoogleSearch
from dotenv import load_dotenv
import os
import json

load_dotenv()

def get_flights(departure="SLC", arrival="HND", outbound_date="2026-03-06", return_date="2026-03-22", outbound_times="17,23"):
    params = {
        "api_key": os.getenv("API_KEY"),
        "engine": "google_flights",
        "show_hidden": "true",
        "deep_search": "true",
        "type": "1",
        "departure_id": departure,
        "arrival_id": arrival,
        "hl": "en",
        "gl": "us",
        "currency": "USD",
        "outbound_date": outbound_date,
        "outbound_times": outbound_times,
        "return_date": return_date,
        "travel_class": "1",
        "sort_by": "2"
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    
    with open("flights.json","w") as f:
        json.dump(results, f, indent=4)
