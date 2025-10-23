import os
from pathlib import Path
from picker import pick_city_pandas
from image_fetcher import compose_image_queries, fetch_images
from wiki_fetcher import fetch_summary, save_wiki_data

BASE_DIR = "data/cities"

def sanitize_name(name: str):
    """Make a folder-safe city name."""
    return "".join(c for c in name if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")

def collect_city():
    # --- Step 1: Pick a city ---
    city_data = pick_city_pandas()
    city_name = sanitize_name(city_data["city"])
    country = city_data.get("country", "")
    lat, lng = city_data.get("lat"), city_data.get("lng")

    print(f"[INFO] Collecting data for: {city_name}, {country}")

    # --- Step 2: Wikipedia data ---
    wiki_data = fetch_summary(city_data["city_ascii"], country)
    save_wiki_data(city_name, wiki_data, BASE_DIR)

    # --- Step 3: Image queries ---
    queries = compose_image_queries(city_data["city_ascii"], country, lat, lng)
    image_paths, source_urls = fetch_images(queries, city_name=city_name, needed=5, base_dir=BASE_DIR)

    if not image_paths:
        print(f"[WARN] No images downloaded for {city_name}.")
    else:
        print(f"[INFO] {len(image_paths)} images saved for {city_name}.")

    return {
        "city": city_name,
        "country": country,
        "wiki": wiki_data,
        "images": image_paths,
        "sources": source_urls
    }

# --- Standalone test ---
if __name__ == "__main__":
    data = collect_city()
    print("\nCollected Data:")
    print(f"City: {data['city']}, Country: {data['country']}")
    print(f"Wiki Title: {data['wiki']['title']}")
    print(f"Images: {data['images']}")
