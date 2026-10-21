import { useState, type FormEvent } from "react";
import {
  getRecommendations,
  type RecommendationsResponse,
} from "./services/api";
import "./App.css";

function App() {
  const [city, setCity] = useState("");
  const [data, setData] = useState<RecommendationsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const destination = city.trim();

    if (destination.length < 2) {
      setError("Please enter a valid destination.");
      return;
    }

    setLoading(true);
    setError(null);
    setData(null);

    try {
      const results = await getRecommendations(destination);
      setData(results);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="site-header">
        <a href="/" className="logo">
          elsewhere<span>.</span>
        </a>

        <span className="header-tagline">
          A better way to discover.
        </span>
      </header>

      <main>
        <section className="hero">
          <div className="hero-content">
            <span className="eyebrow">THE ART OF EXPLORING</span>

            <h1>
              Find your
              <br />
              <em>elsewhere.</em>
            </h1>

            <p className="hero-description">
              Every destination has a story.
              Discover remarkable places and experiences
              thoughtfully curated around the weather.
            </p>

            <form onSubmit={handleSearch} className="search-form">
              <label htmlFor="destination">
                WHERE TO?
              </label>

              <div className="search-container">
                <input
                  id="destination"
                  type="text"
                  placeholder="Florence, Italy"
                  value={city}
                  onChange={(event) => setCity(event.target.value)}
                  maxLength={100}
                  disabled={loading}
                />

                <button type="submit" disabled={loading}>
                  {loading ? "Exploring..." : "Explore →"}
                </button>
              </div>
            </form>

            <div className="hero-footer">
              <span>DISCOVER MORE. PLAN LESS.</span>
              <span>✦</span>
            </div>
          </div>

          <div className="hero-image">
            <div className="image-overlay">
              <span>THE WORLD IS WAITING</span>
              <p>Go somewhere wonderful.</p>
            </div>
          </div>
        </section>

        {loading && (
          <section className="status-section" role="status">
            <div className="spinner" />
            <h2>Finding your somewhere...</h2>
            <p>Discovering experiences worth exploring.</p>
          </section>
        )}

        {error && (
          <section className="status-section error-section" role="alert">
            <h2>We hit a little detour.</h2>
            <p>{error}</p>
            <button onClick={() => setError(null)}>
              Dismiss
            </button>
          </section>
        )}

        {data && (
          <section className="results-section">
            <div className="results-header">
              <span className="eyebrow">YOUR DESTINATION</span>

              <h2>
                Discover <em>{data.city}</em>
              </h2>

              <p>{data.country}</p>
            </div>

            <div className="weather-banner">
              <div>
                <span className="weather-label">
                  CURRENT CONDITIONS
                </span>
                <h3>{Math.round(data.temperature)}°F</h3>
                <p>
                  Recommendations inspired by today's weather.
                </p>
              </div>

              <div className="weather-symbol">☀</div>
            </div>

            <div className="recommendations-heading">
              <div>
                <span className="eyebrow">
                  CURATED FOR YOU
                </span>
                <h2>Places worth discovering.</h2>
              </div>

              <span className="result-count">
                {data.recommendations.length} experiences
              </span>
            </div>

            {data.recommendations.length === 0 ? (
              <div className="empty-state">
                <h3>No experiences found just yet.</h3>
                <p>Try searching for another destination.</p>
              </div>
            ) : (
              <div className="attractions-grid">
                {data.recommendations.map((attraction, index) => (
                  <article
                    className="attraction-card"
                    key={`${attraction.name}-${index}`}
                  >
                    <div className="card-number">
                      {String(index + 1).padStart(2, "0")}
                    </div>

                    <div className="card-content">
                      <span className="card-category">
                        {attraction.categories[0]
                          ?.split(".")
                          .pop()
                          ?.replaceAll("_", " ") || "Experience"}
                      </span>

                      <h3>{attraction.name}</h3>

                      <p className="card-address">
                        {attraction.address}
                      </p>

                      <div className="recommendation-reason">
                        <span>✦</span>
                        <p>{attraction.reason}</p>
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </section>
        )}
      </main>

      <footer className="site-footer">
        <span>elsewhere.</span>
        <p>Made for the curious.</p>
        <span>© 2026 ELSEWHERE</span>
      </footer>
    </div>
  );
}

export default App;