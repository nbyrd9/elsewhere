from recommendations import recommend_attractions


def test_rainy_weather_prioritizes_museums():
    attractions = [
        {
            "name": "Boboli Gardens",
            "categories": ["leisure.park"]
        },
        {
            "name": "Uffizi Gallery",
            "categories": ["entertainment.museum"]
        }
    ]

    results = recommend_attractions(attractions, weather_code=61)

    assert results[0]["name"] == "Uffizi Gallery"
    assert results[0]["score"] == 10
    assert results[1]["score"] == 5


def test_clear_weather_prioritizes_outdoor_attractions():
    attractions = [
        {
            "name": "Uffizi Gallery",
            "categories": ["entertainment.museum"]
        },
        {
            "name": "Boboli Gardens",
            "categories": ["leisure.park"]
        }
    ]

    results = recommend_attractions(attractions, weather_code=0)

    assert results[0]["name"] == "Boboli Gardens"
    assert results[0]["score"] == 10


def test_empty_attractions_returns_empty_list():
    results = recommend_attractions([], weather_code=0)

    assert results == []