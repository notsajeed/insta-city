# src/main.py (conceptual)
from picker import pick_city_pandas, save_posted
from wiki_fetcher import fetch_summary
from image_fetcher import fetch_images, compose_image_queries
from video_builder import build_video
from poster_graph import upload_video_to_ig

def run_once():
    ctx = pick_city_pandas('cities.csv')
    query_city = ctx['city_ascii']
    country = ctx['country']
    wiki = fetch_summary(query_city, country)
    queries = compose_image_queries(query_city, country, ctx['lat'], ctx['lng'])
    images, image_meta = fetch_images(queries, needed=5)  # implement provider fallback inside
    title = wiki['title']
    facts = wiki['summary'][:200]
    video_path = build_video(images, title, facts)
    caption = (f"{title} — Info: {wiki.get('url','Wikipedia')}\n"
               f"{facts}\nImages: {', '.join([m['provider'] for m in image_meta])}\n#travel #city")
    res = upload_video_to_ig(video_path, caption)
    # log posted
    posted_record = {
        'id': ctx.get('id'),
        'city_ascii': query_city,
        'country': country,
        'lat': ctx.get('lat'),
        'lng': ctx.get('lng'),
        'wiki_url': wiki.get('url'),
        'image_sources': image_meta,
        'ig_post_result': res
    }
    save_posted(posted_record)

if __name__ == '__main__':
    run_once()
