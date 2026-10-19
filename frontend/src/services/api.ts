export interface Attraction {
  name: string;
  categories: string[];
  address: string;
  distance: number | null;
  latitude: number;
  longitude: number;
  score: number;
  reason: string;
}

export interface RecommendationsResponse {
  city: string;
  country: string;
  temperature: number;
  weather_code: number;
  recommendations: Attraction[];
}

const API_URL = "/api";

export async function getRecommendations(
  city: string
): Promise<RecommendationsResponse> {
  const response = await fetch(
    `${API_URL}/recommendations?city=${encodeURIComponent(city)}`
  );

  if (!response.ok) {
    const error = await response.json().catch(() => null);

    throw new Error(
      error?.detail || "Unable to retrieve recommendations."
    );
  }

  return response.json();
}