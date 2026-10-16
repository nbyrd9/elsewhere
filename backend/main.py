import httpx
from fastapi import FastAPI, HTTPException, Query

import os
from dotenv import load_dotenv

load_dotenv()

GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")

app = FastAPI(
    title="Elsewhere API",
    description="Weather-aware travel recommendations",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Welcome to Elsewhere!",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }

@app.get("/weather")
async def get_weather(
    city: str = Query(min_length=2, max_length=100)
):
    async with httpx.AsyncClient(timeout=10.0) as client:

        # Step 1: Convert city name into coordinates
        geo_response = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": city,
                "count": 1
            }
        )
        geo_response.raise_for_status()

        locations = geo_response.json().get("results", [])

        if not locations:
            raise HTTPException(
                status_code=404,
                detail="City not found"
            )

        location = locations[0]

        # Step 2: Retrieve weather using coordinates
        weather_response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "current": "temperature_2m,weather_code",
                "timezone": "auto"
            }
        )
        weather_response.raise_for_status()

        weather = weather_response.json()["current"]

        return {
            "city": location["name"],
            "country": location["country"],
            "temperature": weather["temperature_2m"],
            "weather_code": weather["weather_code"]
        }