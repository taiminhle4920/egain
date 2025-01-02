from flask import Flask, render_template, request
from geopy.geocoders import Nominatim
import requests
from dotenv import load_dotenv
import os
import google.generativeai as genai
import json


app = Flask(__name__)

geolocator = Nominatim(user_agent="geoapi")
load_dotenv()
ai_api_key = os.getenv("AI_API_KEY")
rapid_api_key = os.getenv("RAPID_API_KEY")
genai.configure(api_key=ai_api_key)
model = genai.GenerativeModel("gemini-1.5-flash")
rapid_api_host = "zillow-com1.p.rapidapi.com"
url = "https://zillow-com1.p.rapidapi.com/property"

# Validate address using Nominatim
def geocode_address(address):
    location = geolocator.geocode(address)
    if location:
        return True
    return False

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
    
    # validate address
    if not geocode_address(full_address):
        return "Invalid address", 400

    querystring = {"address": full_address}

    headers = {
	"x-rapidapi-key": rapid_api_key,
	"x-rapidapi-host": rapid_api_host
    }
    response = requests.get(url, headers=headers, params=querystring)

    # Prompt engineering and generate response using Google Gemini
    prompt = (
        "For this address: "
        + full_address
        +"Give a summary about the property of the address, such as lot size, bathroom, bedrooms, nearby schools, estimated value, etc."
        + json.dumps(response.json())
    )
    response = model.generate_content(prompt)

    return response.text, 200  
    


if __name__ == "__main__":
    app.run(debug=True)
