import httpx
from fastapi import FastAPI, HTTPException, Query

import os
from dotenv import load_dotenv
from recommendations import recommend_attractions
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")

app = FastAPI(
    title="Elsewhere API",
    description="Weather-aware travel recommendations",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
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
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "temperature": weather["temperature_2m"],
            "weather_code": weather["weather_code"]
        }

@app.get("/attractions")
async def get_attractions(
    latitude: float = Query(ge=-90, le=90),
    longitude: float = Query(ge=-180, le=180)
):
    if not GEOAPIFY_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Attractions service is not configured"
        )

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.geoapify.com/v2/places",
                params={
                    "categories": "tourism.attraction,entertainment.museum",
                    "filter": f"circle:{longitude},{latitude},5000",
                    "bias": f"proximity:{longitude},{latitude}",
                    "limit": 20,
                    "apiKey": GEOAPIFY_API_KEY
                }
            )

            response.raise_for_status()

            data = response.json()

            attractions = []

            for feature in data.get("features", []):
                properties = feature.get("properties", {})

                if not properties.get("name"):
                    continue

                attractions.append({
                    "name": properties["name"],
                    "categories": properties.get("categories", []),
                    "address": properties.get("formatted", ""),
                    "distance": properties.get("distance"),
                    "latitude": properties.get("lat"),
                    "longitude": properties.get("lon")
                })

            return {
                "total": len(attractions),
                "attractions": attractions
            }

    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 429:
            raise HTTPException(
                status_code=503,
                detail="Attractions service is temporarily rate-limited"
            ) from exc

        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve attractions"
        ) from exc

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail="Attractions service is temporarily unavailable"
        ) from exc

@app.get("/recommendations")
async def get_recommendations(
    city: str = Query(min_length=2, max_length=100)
):
    # Get weather and location data
    weather_data = await get_weather(city)

    latitude = weather_data["latitude"]
    longitude = weather_data["longitude"]

    # Get nearby attractions
    attractions_data = await get_attractions(
        latitude=latitude,
        longitude=longitude
    )

    # Rank attractions based on weather
    recommendations = recommend_attractions(
        attractions_data["attractions"],
        weather_data["weather_code"]
    )

    return {
        "city": weather_data["city"],
        "country": weather_data["country"],
        "temperature": weather_data["temperature"],
        "weather_code": weather_data["weather_code"],
        "recommendations": recommendations
    }