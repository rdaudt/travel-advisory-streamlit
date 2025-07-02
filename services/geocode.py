import requests
from functools import lru_cache

@lru_cache(maxsize=256)
def validate_city_country(city: str, country: str) -> dict:
    """
    Uses OSM Nominatim to check if `city` exists in `country`.
    Returns:
      { valid: bool, ambiguous: bool }
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": f"{city}, {country}",
        "format": "json",
        "addressdetails": 1,
        "limit": 5,
    }
    headers = {
        "User-Agent": "travel-advisory-assistant/1.0 (your-email@example.com)"
    }
    resp = requests.get(url, params=params, headers=headers, timeout=5)
    resp.raise_for_status()
    results = resp.json()

    if not results:
        return {"valid": False, "ambiguous": False}

    # filter those where the `address` block’s country matches exactly
    matches = [r for r in results
               if r.get("address", {}).get("country", "").lower() == country.lower()]

    if not matches:
        # results found, but none in the requested country
        return {"valid": False, "ambiguous": False}

    # If more than one match but in different states/provinces, it’s ambiguous
    provinces = {r["address"].get("state") or r["address"].get("county")
                 for r in matches}
    ambiguous = len(provinces) > 1

    return {"valid": True, "ambiguous": ambiguous}
