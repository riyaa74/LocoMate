from flask import Flask
from config import secrets
import requests

def search_places(api_key, location, category, radius=5000, max_results=1):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "key": api_key,
        "location": f"{location['lat']},{location['lng']}",
        "radius": radius,
        "type": category 
    }
    
    response = requests.get(url, params=params)
    places_data = response.json()
    return places_data.get('results', [])[:max_results]

def format_place_data(places_data):
    formatted_places = []

    for category, places in places_data.items():
        for place in places:
            formatted_place = {
                "name": place.get("name"),
                "rating": place.get("rating"),
                "vicinity": place.get("vicinity"),
                "types": ", ".join(place.get("types", [])),
                #"open_now": place.get("opening_hours", {}).get("open_now", "N/A"),
                "location": {
                    "lat": place["geometry"]["location"]["lat"],
                    "lng": place["geometry"]["location"]["lng"]
                },
                #"photo": place["photos"][0]["html_attributions"][0] if place.get("photos") else None
            }
            formatted_places.append(formatted_place)
    
    return formatted_places

def get_lat_lon_google(place_name, api_key):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": place_name,
        "key": api_key
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if data["results"]:
        location = data["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]
    else:
        return None

# categories = ["park", "restaurant", "museum"]
# location = {"lat": 40.7128, "lng": -74.0060}  # New York City
# api_key = secrets.PLACES_API_KEY

#places_results = {cat: search_places(api_key, location, cat) for cat in categories}
#print(places_results)
