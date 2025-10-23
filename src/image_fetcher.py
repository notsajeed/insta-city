# src/image_fetcher.py
import os
import requests
from pathlib import Path
from urllib.parse import urlparse
from time import sleep
from dotenv import load_dotenv

load_dotenv()

PEXELS_KEY = os.getenv("PEXELS_API_KEY")
CACHE_DIR = Path("cache/images")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def _safe_get(url, headers=None, params=None):
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        if res.status_code == 429:
            print("[WARN] Rate limited, sleeping 10s...")
            sleep(10)
            return _safe_get(url, headers, params)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"[ERROR] _safe_get: {e}")
        return None

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

def fetch_images(queries, city_name=None, needed=5, base_dir="data/cities"):
    """
    Fetch images from Pexels and store them locally as photo1.jpeg, photo2.jpeg, etc.
    Returns:
        (list_of_local_paths, list_of_source_urls)
    """
    all_images = []

    for q in queries:
        print(f"[INFO] Searching images for '{q}'...")
        r = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": PEXELS_KEY},
            params={"query": q, "per_page": needed},
            timeout=10
        )
        if r.status_code != 200:
            print(f"[WARN] Pexels request failed for {q}: {r.status_code}")
            continue
        data = r.json()
        photos = data.get("photos", [])
        for p in photos:
            all_images.append({
                "url": p["src"]["large2x"],
                "photographer": p["photographer"],
                "source": p["url"]
            })

    # Remove duplicates
    unique_images = list({img["url"]: img for img in all_images}.values())
    if not unique_images:
        print("[ERROR] No images found for any query.")
        return [], []

    # Prepare directories
    city_folder = city_name.replace(" ", "_") if city_name else "unknown_city"
    images_dir = Path(base_dir) / city_folder / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    downloaded_paths = []
    for idx, img in enumerate(unique_images[:needed], start=1):
        url = img["url"]
        path = images_dir / f"photo{idx}.jpg"
        if path.exists():
            downloaded_paths.append(str(path))
            continue
        try:
            with requests.get(url, stream=True, timeout=10) as r:
                if r.status_code == 200:
                    with open(path, "wb") as f:
                        for chunk in r.iter_content(1024):
                            f.write(chunk)
                    downloaded_paths.append(str(path))
                else:
                    print(f"[WARN] Failed to download {url}: {r.status_code}")
        except Exception as e:
            print(f"[WARN] Error downloading {url}: {e}")

    if len(downloaded_paths) < needed:
        downloaded_paths = (downloaded_paths * ((needed // len(downloaded_paths)) + 1))[:needed]
        print(f"[WARN] Only {len(downloaded_paths)} images found; duplicating to reach {needed}.")

    print(f"[INFO] Downloaded {len(downloaded_paths)} images for {city_name} → {images_dir}")
    return downloaded_paths, [img["url"] for img in unique_images]

# Example test
if __name__ == "__main__":
    queries = compose_image_queries("Tokyo", "Japan")
    images, meta = fetch_images(queries, city_name="Tokyo", needed=5)
    print("Local images:", images)
    print("Original URLs:", meta)
