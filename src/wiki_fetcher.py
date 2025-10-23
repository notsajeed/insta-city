# src/wiki_fetcher.py
import wikipedia
import json
from pathlib import Path

wikipedia.set_lang("en")


def safe_search(query, max_results=5):
    """Wrapper around wikipedia.search() that never crashes."""
    try:
        return wikipedia.search(query, results=max_results)
    except Exception:
        return []


def split_text(text, max_chars=100):
    """
    Split text into chunks of roughly max_chars characters.
    Tries to split at word boundaries.
    """
    words = text.split()
    chunks = []
    current_chunk = []
    char_count = 0

    for word in words:
        char_count += len(word) + 1 
        if char_count > max_chars:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            char_count = len(word) + 1
        else:
            current_chunk.append(word)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def fetch_summary(city_ascii, country="", sentences=5, max_chars_per_chunk=100):
    """
    Fetch Wikipedia summary + page info for a city.
    Returns dict: { title, summary, chunks, url }
    """
    query = f"{city_ascii}, {country}" if country else city_ascii
    try:
        results = safe_search(query)
        title = results[0] if results else city_ascii
        summary = wikipedia.summary(title, sentences=sentences)
        page = wikipedia.page(title, auto_suggest=False)

        chunks = split_text(summary, max_chars=max_chars_per_chunk)

        return {
            "title": page.title,
            "summary": summary,
            "chunks": chunks, 
            "url": page.url,
        }

    except wikipedia.exceptions.DisambiguationError as e:
        opts = e.options
        # Try to find a match including country
        if country:
            for o in opts:
                if country.lower() in o.lower():
                    return fetch_summary(o, "", sentences=sentences, max_chars_per_chunk=max_chars_per_chunk)
        # fallback to first option
        return fetch_summary(opts[0], "", sentences=sentences, max_chars_per_chunk=max_chars_per_chunk)

    except Exception as e:
        print(f"[WARN] Wikipedia fetch failed for '{city_ascii}': {e}")
        return {"title": city_ascii, "summary": "", "chunks": [], "url": ""}


def save_wiki_data(city_name, data, base_dir="data/cities"):
    """
    Saves Wikipedia info to JSON file under data/cities/<city>/wiki.json
    """
    city_dir = Path(base_dir) / city_name.replace(" ", "_")
    city_dir.mkdir(parents=True, exist_ok=True)
    wiki_path = city_dir / "wiki.json"

    with open(wiki_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[INFO] Saved wiki data for {city_name} → {wiki_path}")
    return wiki_path

