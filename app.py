from flask import Flask, render_template, request
from geopy.geocoders import Nominatim
from serpapi import GoogleSearch
import requests
from dotenv import load_dotenv
import os
import google.generativeai as genai
import json


app = Flask(__name__)

OVERPASS_API_URL = "https://overpass-api.de/api/interpreter"
geolocator = Nominatim(user_agent="geoapi")
load_dotenv()
ai_api_key = os.getenv("AI_API_KEY")
serpapi_key = os.getenv("SERPAPI_KEY")
genai.configure(api_key=ai_api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Validate address using Nominatim
def geocode_address(address):
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    return None, None

# Get nearby school within 10km radius using Overpass API
def get_nearby_schools(lat, lon, radius=10000):
    query = f"""
    [out:json];
    node
      ["amenity"="school"]
      (around:{radius},{lat},{lon});
    out;
    """
    response = requests.get(OVERPASS_API_URL, params={"data": query})
    return response.json()

# Search house information using SerpAPI
def get_house_info(address):

    query = "get house information of this address" + address
    
    search = GoogleSearch({
        "q": query,
        "api_key": serpapi_key,
    })
    results = search.get_dict()
    return results

@app.route("/")
def index():
    return render_template("index.html")



@app.route("/search", methods=["POST"])
def search_property():
    house_number = request.form["house_number"]
    street = request.form["street"]
    city = request.form["city"]
    state = request.form["state"]
    zip_code = request.form["zip_code"]

    full_address = f"{house_number} {street}, {city}, {state}, {zip_code}"

    # Geocode the address to get latitude and longitude
    latitude, longitude = geocode_address(full_address)

    if not latitude or not longitude:
        return "Not a valid address.", 400 


    # Fetch necessary data
    school_data = get_nearby_schools(latitude, longitude)
    search_data = get_house_info(full_address)

    # Prompt engineering and generate response using Google Gemini
    prompt = (
        "For this address: "
        + full_address
        +"Give a summary about the property of the address, such as lot size, bathroom, bedrooms, etc."
        + json.dumps(search_data)
        +"knowing that these schools are confirmed nearby, please list all the name of school with the response."
        + json.dumps(school_data["elements"])
    )
    response = model.generate_content(prompt)

    return response.text, 200  
    


if __name__ == "__main__":
    app.run(debug=True)
