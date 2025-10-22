# src/image_fetcher.py
import os
import requests
import random
import json
from pathlib import Path
from time import sleep
from dotenv import load_dotenv

load_dotenv()

CACHE_DIR = Path("cache/images")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# --- ENV KEYS ---
PEXELS_KEY = os.getenv("PEXELS_API_KEY")
UNSPLASH_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
PIXABAY_KEY = os.getenv("PIXABAY_API_KEY")

# --- UTILITIES ---
def _safe_get(url, headers=None, params=None):
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        if res.status_code == 429:  # rate limit
            print("[WARN] Rate limited, sleeping 10s...")
            sleep(10)
            return _safe_get(url, headers, params)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"[ERROR] {_safe_get.__name__}: {e}")
        return None

def _cache_path(query):
    return CACHE_DIR / f"{query.replace(' ', '_').lower()}.json"

def _load_cache(query):
    path = _cache_path(query)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def _save_cache(query, data):
    path = _cache_path(query)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- PROVIDER QUERIES ---
def fetch_from_pexels(query, per_page=10):
    if not PEXELS_KEY:
        return []
    headers = {"Authorization": PEXELS_KEY}
    params = {"query": query, "per_page": per_page}
    data = _safe_get("https://api.pexels.com/v1/search", headers, params)
    if not data or "photos" not in data:
        return []
    return [
        {
            "url": p["src"]["original"],
            "thumb": p["src"]["medium"],
            "photographer": p["photographer"],
            "provider": "Pexels",
            "source_url": p["url"]
        }
        for p in data["photos"]
    ]

def fetch_from_unsplash(query, per_page=10):
    if not UNSPLASH_KEY:
        return []
    headers = {"Accept-Version": "v1", "Authorization": f"Client-ID {UNSPLASH_KEY}"}
    params = {"query": query, "per_page": per_page}
    data = _safe_get("https://api.unsplash.com/search/photos", headers, params)
    if not data or "results" not in data:
        return []
    return [
        {
            "url": p["urls"]["regular"],
            "thumb": p["urls"]["thumb"],
            "photographer": p["user"]["name"],
            "provider": "Unsplash",
            "source_url": p["links"]["html"]
        }
        for p in data["results"]
    ]

def fetch_from_pixabay(query, per_page=10):
    if not PIXABAY_KEY:
        return []
    params = {"key": PIXABAY_KEY, "q": query, "image_type": "photo", "per_page": per_page}
    data = _safe_get("https://pixabay.com/api/", params=params)
    if not data or "hits" not in data:
        return []
    return [
        {
            "url": p["largeImageURL"],
            "thumb": p["previewURL"],
            "photographer": p.get("user", "Unknown"),
            "provider": "Pixabay",
            "source_url": p.get("pageURL", "")
        }
        for p in data["hits"]
    ]

# --- MAIN FETCH LOGIC ---
def compose_image_queries(city_ascii, country, lat=None, lng=None):
    queries = []
    if city_ascii and country:
        queries.extend([
            f"{city_ascii} skyline {country}",
            f"{city_ascii} {country} landmarks",
            f"{city_ascii} {country} city",
        ])
    elif city_ascii:
        queries.extend([
            f"{city_ascii} skyline",
            f"{city_ascii} city",
        ])
    if lat and lng:
        queries.append(f"{city_ascii} {lat},{lng}")
    return queries

def fetch_images(queries, needed=5):
    """
    Try Pexels -> Unsplash -> Pixabay in order.
    Caches successful queries.
    Returns (image_urls, metadata_list)
    """
    all_images = []
    seen = set()

    for query in queries:
        cache_data = _load_cache(query)
        if cache_data:
            provider_images = cache_data
        else:
            provider_images = []
            print(f"[INFO] Searching images for '{query}'...")

            for fn in [fetch_from_pexels, fetch_from_unsplash, fetch_from_pixabay]:
                imgs = fn(query)
                if imgs:
                    provider_images = imgs
                    break  # stop after first provider success

            if provider_images:
                _save_cache(query, provider_images)

        # merge dedup
        for img in provider_images:
            if img["url"] not in seen:
                all_images.append(img)
                seen.add(img["url"])

        if len(all_images) >= needed:
            break

    # fallback: random filler if still short
    if len(all_images) < needed:
        if len(all_images) == 0:
            print("[ERROR] No images found for any query — check your API keys or query text.")
            return [], []
        print("[WARN] Not enough images found, duplicating existing ones")
        all_images = (all_images * ((needed // max(len(all_images), 1)) + 1))[:needed]


    return [img["url"] for img in all_images[:needed]], all_images[:needed]


# Example test
if __name__ == "__main__":
    q = compose_image_queries("Tokyo", "Japan")
    urls, meta = fetch_images(q, needed=5)
    print("\nFetched URLs:\n", urls)
    print("\nMetadata:\n", json.dumps(meta, indent=2))
