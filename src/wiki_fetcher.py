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


def fetch_summary(city_ascii, country="", sentences=3):
    """
    Fetch Wikipedia summary + page info for a given city.
    Tries to handle small cities, disambiguation, and missing pages.
    Returns dict: { title, summary, url }
    """
    query = f"{city_ascii}, {country}" if country else city_ascii

    try:
        results = safe_search(query)
        if not results:
            return {
                "title": city_ascii,
                "summary": f"No Wikipedia summary found for {city_ascii}.",
                "url": "",
            }

        # Prefer exact match first
        title = next(
            (r for r in results if city_ascii.lower() in r.lower()), results[0]
        )

        summary = wikipedia.summary(title, sentences=sentences)
        page = wikipedia.page(title, auto_suggest=False)

        # If summary is too short, try to extend using related pages
        if len(summary.split()) < 20:
            extra = fetch_extended_summary(city_ascii, country, sentences)
            summary += " " + extra

        return {"title": page.title, "summary": summary, "url": page.url}

    except wikipedia.exceptions.DisambiguationError as e:
        opts = e.options
        # Prefer options containing the country
        filtered = [o for o in opts if country.lower() in o.lower()] if country else opts
        if filtered:
            return fetch_summary(filtered[0], "", sentences=sentences)
        # fallback to first option
        return fetch_summary(opts[0], "", sentences=sentences)

    except Exception as e:
        print(f"[WARN] Wikipedia fetch failed for '{city_ascii}': {e}")
        return {
            "title": city_ascii,
            "summary": f"No Wikipedia summary available for {city_ascii}.",
            "url": "",
        }


def fetch_extended_summary(city_ascii, country="", sentences=2):
    """
    Attempt to fetch additional info from related pages like history or landmarks.
    Useful for small cities with very short main pages.
    """
    extra_summary = ""
    search_terms = [f"{city_ascii} history", f"{city_ascii} landmarks"]

    for term in search_terms:
        try:
            s = safe_search(term)
            if s:
                extra_summary += " " + wikipedia.summary(s[0], sentences=sentences)
        except Exception:
            continue

    return extra_summary.strip()


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
    city, country = "Salem", "United States"
    data = fetch_summary(city, country)
    save_wiki_data(city, data)
    print(json.dumps(data, indent=2))
