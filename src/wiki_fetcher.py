# src/wiki_fetcher.py
import wikipedia
import json
from pathlib import Path

wikipedia.set_lang('en')

def safe_search(query, max_results=5):
    """Wrapper around wikipedia.search() that never crashes."""
    try:
        return wikipedia.search(query, results=max_results)
    except Exception:
        return []

def fetch_summary(city_ascii, country='', sentences=3):
    """
    Fetch Wikipedia summary + page info for a given city.
    Returns dict: { title, summary, url }
    """
    query = f"{city_ascii}, {country}" if country else city_ascii

    try:
        results = safe_search(query)
        title = results[0] if results else city_ascii
        summary = wikipedia.summary(title, sentences=sentences)
        page = wikipedia.page(title, auto_suggest=False)
        return {
            'title': page.title,
            'summary': summary,
            'url': page.url
        }

    except wikipedia.exceptions.DisambiguationError as e:
        opts = e.options
        if country:
            for o in opts:
                if country.lower() in o.lower():
                    return fetch_summary(o, '', sentences=sentences)
        return fetch_summary(opts[0], '', sentences=sentences)

    except Exception as e:
        print(f"[WARN] Wikipedia fetch failed for '{city_ascii}': {e}")
        return {'title': city_ascii, 'summary': '', 'url': ''}

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

# Example standalone test
if __name__ == "__main__":
    city, country = "Tokyo", "Japan"
    data = fetch_summary(city, country)
    save_wiki_data(city, data)
    print(json.dumps(data, indent=2))
