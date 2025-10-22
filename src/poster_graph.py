# src/poster_graph.py
import requests
import time
import os
import json

GRAPH_URL = "https://graph.facebook.com/v21.0"

# set these as environment variables or in a .env file
IG_ACCOUNT_ID = os.getenv("IG_ACCOUNT_ID")
ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")

def _handle_response(resp):
    try:
        resp.raise_for_status()
        return resp.json()
    except requests.HTTPError as e:
        print(f"[ERROR] Graph API request failed: {e}")
        try:
            print(resp.json())
        except Exception:
            print(resp.text)
        raise

def upload_video_to_ig(video_path, caption, cover_url=None, is_reel=True):
    """
    Uploads a video to Instagram via Graph API.
    Supports Reels (recommended) or Feed videos.
    """
    if not IG_ACCOUNT_ID or not ACCESS_TOKEN:
        raise ValueError("Missing IG_ACCOUNT_ID or ACCESS_TOKEN in environment")

    # Step 1: Upload container
    endpoint = f"{GRAPH_URL}/{IG_ACCOUNT_ID}/media"
    upload_type = "REELS" if is_reel else "CONTAINER"

    params = {
        "media_type": "VIDEO",
        "video_url": None,  # we'll upload file manually below
        "caption": caption,
        "access_token": ACCESS_TOKEN
    }

    # Upload video directly
    print("[INFO] Uploading video to Instagram container...")
    with open(video_path, 'rb') as f:
        files = {'file': (os.path.basename(video_path), f, 'video/mp4')}
        res = requests.post(endpoint, data=params, files=files)
    data = _handle_response(res)
    upload_id = data.get('id')

    if not upload_id:
        raise RuntimeError(f"Upload failed: {data}")

    print(f"[INFO] Video upload container created: {upload_id}")

    # Step 2: Publish container
    publish_endpoint = f"{GRAPH_URL}/{IG_ACCOUNT_ID}/media_publish"
    publish_params = {
        "creation_id": upload_id,
        "access_token": ACCESS_TOKEN
    }

    print("[INFO] Publishing video...")
    res = requests.post(publish_endpoint, data=publish_params)
    publish_data = _handle_response(res)

    ig_post_id = publish_data.get('id')
    if not ig_post_id:
        raise RuntimeError(f"Publish failed: {publish_data}")

    print(f"[SUCCESS] Video published: https://www.instagram.com/p/{ig_post_id}/")
    return {"upload_id": upload_id, "ig_post_id": ig_post_id, "response": publish_data}


def refresh_long_lived_token(app_id=None, app_secret=None):
    """
    Refreshes long-lived tokens (valid 60 days).
    Call this weekly via cron or GitHub Actions.
    """
    if not app_id or not app_secret or not ACCESS_TOKEN:
        raise ValueError("Missing app_id, app_secret, or ACCESS_TOKEN")

    url = f"{GRAPH_URL}/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": ACCESS_TOKEN
    }

    print("[INFO] Refreshing long-lived token...")
    res = requests.get(url, params=params)
    data = _handle_response(res)
    new_token = data.get("access_token")
    if new_token:
        print("[INFO] Token refreshed successfully.")
        with open(".env", "a") as f:
            f.write(f"\nIG_ACCESS_TOKEN={new_token}\n")
    return new_token
