def recommend_attractions(attractions: list, weather_code: int) -> list:
    """Rank attractions based on current weather conditions."""

    # Open-Meteo weather codes for precipitation and thunderstorms
    rainy_codes = {
        51, 53, 55, 56, 57,
        61, 63, 65, 66, 67,
        71, 73, 75, 77,
        80, 81, 82, 85, 86,
        95, 96, 99
    }

    is_rainy = weather_code in rainy_codes

    recommendations = []

    for attraction in attractions:
        categories = attraction.get("categories", [])

        is_indoor = any(
            "museum" in category
            for category in categories
        )

        if is_rainy:
            score = 10 if is_indoor else 5
            reason = (
                "A great indoor option for rainy weather."
                if is_indoor
                else "Worth exploring if the weather improves."
            )
        else:
            score = 10 if not is_indoor else 8
            reason = (
                "A great place to explore in pleasant weather."
                if not is_indoor
                else "A cultural experience worth visiting."
            )

        recommendations.append({
            **attraction,
            "score": score,
            "reason": reason
        })

    return sorted(
        recommendations,
        key=lambda item: item["score"],
        reverse=True
    )