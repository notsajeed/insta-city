# src/wiki_fetcher.py
import wikipedia
wikipedia.set_lang('en')

def safe_search(query, max_results=5):
    try:
        return wikipedia.search(query, results=max_results)
    except Exception:
        return []

def fetch_summary(city_ascii, country='', sentences=3):
    query = f"{city_ascii}, {country}" if country else city_ascii
    # try exact query first, then fallback to search suggestions
    try:
        results = safe_search(query)
        # if exact title found, use it; else try first useful result
        title = results[0] if results else city_ascii
        summary = wikipedia.summary(title, sentences=sentences)
        page = wikipedia.page(title, auto_suggest=False)
        return {
            'title': page.title,
            'summary': summary,
            'url': page.url
        }
    except wikipedia.exceptions.DisambiguationError as e:
        # pick option that contains the country name if available
        opts = e.options
        if country:
            for o in opts:
                if country.lower() in o.lower():
                    return fetch_summary(o, '', sentences=sentences)
        # fallback to first option
        return fetch_summary(opts[0], '', sentences=sentences)
    except Exception:
        # gentle fallback to empty content
        return {'title': city_ascii, 'summary': '', 'url': ''}
