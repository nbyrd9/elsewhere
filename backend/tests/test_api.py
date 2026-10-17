import pytest
import httpx
import respx
from fastapi import HTTPException

import main


@pytest.mark.asyncio
@respx.mock
async def test_geoapify_rate_limit(monkeypatch):
    """Verify that Geoapify rate limits produce a helpful error."""

    monkeypatch.setattr(main, "GEOAPIFY_API_KEY", "test-key")

    respx.get(
        "https://api.geoapify.com/v2/places"
    ).mock(
        return_value=httpx.Response(
            429,
            json={"message": "Rate limit exceeded"}
        )
    )

    with pytest.raises(HTTPException) as exc:
        await main.get_attractions(
            latitude=43.7696,
            longitude=11.2558
        )

    assert exc.value.status_code == 503
    assert "rate-limited" in exc.value.detail


@pytest.mark.asyncio
@respx.mock
async def test_geoapify_server_error(monkeypatch):
    """Verify that an upstream server error is handled."""

    monkeypatch.setattr(main, "GEOAPIFY_API_KEY", "test-key")

    respx.get(
        "https://api.geoapify.com/v2/places"
    ).mock(
        return_value=httpx.Response(
            500,
            json={"message": "Internal server error"}
        )
    )

    with pytest.raises(HTTPException) as exc:
        await main.get_attractions(
            latitude=43.7696,
            longitude=11.2558
        )

    assert exc.value.status_code == 502
    assert exc.value.detail == "Unable to retrieve attractions"