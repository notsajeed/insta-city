# src/picker.py
import os
import json
import random
import pandas as pd
from pathlib import Path
from datetime import datetime

POSTED_FILE = Path('posted.jsonl') 

def load_posted_set():
    if not POSTED_FILE.exists():
        return set()
    posted = set()
    with POSTED_FILE.open('r', encoding='utf-8') as f:
        for line in f:
            try:
                rec = json.loads(line)
                posted.add(rec.get('id') or f"{rec.get('city')}|{rec.get('country')}")
            except Exception:
                continue
    return posted

def save_posted(record):
    POSTED_FILE.parent.mkdir(parents=True, exist_ok=True)
    record['posted_at'] = datetime.utcnow().isoformat() + 'Z'
    with POSTED_FILE.open('a', encoding='utf-8') as f:
        f.write(json.dumps(record, ensure_ascii=False) + '\n')

def pick_city_pandas(csv_path='worldcities.csv'):
    df = pd.read_csv(csv_path)
    posted = load_posted_set()
    # prefer rows not posted yet
    df['unique_id'] = df.apply(lambda r: str(int(r.get('id'))) if pd.notna(r.get('id')) else f"{r['city_ascii']}|{r.get('country','')}", axis=1)
    not_posted = df[~df['unique_id'].isin(posted)]
    if not not_posted.empty:
        row = not_posted.sample(n=1).iloc[0]
    else:
        # all posted — fallback to random with replacement
        row = df.sample(n=1).iloc[0]
    return {
        'city': row['city'],
        'city_ascii': row['city_ascii'],
        'country': row.get('country',''),
        'lat': row.get('lat'),
        'lng': row.get('lng'),
        'id': int(row['id']) if pd.notna(row.get('id')) else None
    }

# memory-light reservoir sampling for gigantic CSVs
def pick_city_reservoir(csv_path='cities.csv'):
    import csv
    posted = load_posted_set()
    chosen = None
    count = 0
    with open(csv_path, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            unique_id = row.get('id') or f"{row.get('city_ascii')}|{row.get('country','')}"
            if unique_id in posted:
                continue
            count += 1
            # reservoir algorithm: replace with 1/count probability
            if random.randrange(count) == 0:
                chosen = row
    if chosen is None:
        # fallback: read whole file and choose any
        return pick_city_pandas(csv_path)
    return {
        'city': chosen.get('city'),
        'city_ascii': chosen.get('city_ascii'),
        'country': chosen.get('country',''),
        'lat': chosen.get('lat'),
        'lng': chosen.get('lng'),
        'id': int(chosen['id']) if chosen.get('id') else None
    }

# Example usage
if __name__ == '__main__':
    print(pick_city_pandas())  # or pick_city_reservoir()
