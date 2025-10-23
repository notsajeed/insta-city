# src/main.py
from pathlib import Path
from collector import collect_city
from video_builder import build_video
from picker import save_posted

BASE_DIR = Path("data/cities")

def main():
    # --- Collect data for a random city ---
    data = collect_city()
    city_name = data["city"]
    country = data["country"]
    wiki_data = data["wiki"]
    images = data["images"]

    if not images:
        print(f"[ERROR] No images found for {city_name}, skipping.")
        return

    # --- Split wiki summary into chunks for captions ---
    facts_chunks = wiki_data.get("chunks", []) or [wiki_data.get("summary", "")]

    # --- Build the video ---
    output_path = BASE_DIR / city_name / f"{city_name}_reel.mp4"
    try:
        build_video(
            image_paths=images,
            title_text=wiki_data.get("title", city_name),
            facts_chunks=facts_chunks,
            output_path=str(output_path),
            fps=30,
            duration_per_image=3
        )
    except Exception as e:
        print(f"[ERROR] Failed to build video for {city_name}: {e}")
        return

    # --- Mark city as posted ---
    save_posted({
        "city": city_name,
        "country": country,
        "id": None
    })

    print(f"[✅] Finished processing {city_name}.")

if __name__ == "__main__":
    main()
