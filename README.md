
# 🌆 CityForge

**CityForge** is an automated content generation pipeline that **builds short cinematic city videos** using open datasets and free APIs.  
It fetches city facts, gathers visuals, and crafts portrait-style clips, ideal for **Instagram Reels, YouTube Shorts, or TikTok**.

---

## 🚀 Key Features

- 🧠 **Automated Wiki Fetching** – Retrieves concise, readable summaries and metadata for any city using the Wikipedia API.  
- 🏙️ **Smart Visual Collector** – Gathers landscape and skyline imagery via the **Pexels API**.  
- 🎬 **Video Composer** – Blends visuals, title overlays, and key facts into short vertical videos.  
- 🗂️ **Local Caching** – Every fetched city is stored under `data/cities/` for offline use.  
- 🧩 **Extensible Architecture** – Plug in AI summarization, better imagery sources, or custom video templates easily.

---

## 🧭 Example Workflow

```bash
python src/main.py
````

CityForge will:

1. Collect city information (from Wikipedia).
2. Fetch visuals (from Pexels/Wikimedia).
3. Generate a short video clip (1080x1920 portrait).

> Example output:
> `assets/tmp/tokyo_reel.mp4` → cinematic city showcase video.

---

## 🧱 Project Structure

```
cityforge/
│
├── src/
│   ├── main.py              # Main orchestrator
│   ├── collector.py         # Handles data flow and orchestration
│   ├── wiki_fetcher.py      # Grabs summaries + cleans text
│   ├── image_fetcher.py     # Fetches images from APIs
│   ├── video_builder.py     # Builds vertical videos
│   ├── utils.py             # Utility helpers
│
├── data/
│   └── cities/              # City-wise data cache (images + wiki)
│
├── assets/
│   └── tmp/                 # Output videos
│
├── .env                     # API keys
└── README.md
```

---

## 🔧 Setup

### 1️⃣ Clone the repository

```bash
git clone https://github.com/notsajeed/cityforge.git
cd cityforge
```

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Configure your `.env`

```bash
PEXELS_API_KEY=your_pexels_api_key_here
WIKIMEDIA_API_KEY=your_wikimedia_api_key_here  # optional
```

> 🧩 **Pexels API Key:** [Get yours here](https://www.pexels.com/api/)
> 🌍 **City Data Source:** [SimpleMaps World Cities](https://simplemaps.com/data/world-cities)
> 🖼️ **Optional:** Use Google Maps or other imagery APIs for higher accuracy.

---

## ⚙️ Usage Example

```python
python src/main.py
```

It will automatically:

* Fetch data for a given city
* Download related images
* Generate a video in `assets/tmp/`

---

## ⚠️ Current Limitations (and Improvement Opportunities)

CityForge is still in an experimental phase.
Here are a few areas where you can enhance the experience:

* 🪞 **Visual Consistency:**
  Sometimes, Pexels returns unrelated or low-quality city photos.
  → *You can switch to the Google Maps or Wikimedia API for more relevant visuals.*

* 💬 **Text Overflow:**
  Long Wikipedia summaries can overflow in the captions.
  → *Try breaking text into shorter lines or sentences during fetching.*

* 🖋️ **Basic Typography:**
  The default caption font is generic and static.
  → *Use custom fonts, text shadows, or animated overlays to improve visual polish.*

* 🎞️ **Transition Smoothness:**
  Basic fade-in/out is used for now.
  → *You can integrate Framer Motion–style transitions or cinematic zoom/pan effects.*

---

## 🧠 Future Roadmap

* 🤖 AI-powered summarization and captioning
* 🔊 Automated text-to-speech narration
* 🗺️ Map overlays and geolocation visualization
* 📱 One-click social upload pipeline

---

## 🪪 Credits

* **City Data** – [SimpleMaps World Cities Dataset](https://simplemaps.com/data/world-cities)
* **Images** – [Pexels API](https://www.pexels.com/api/) and [Wikimedia Commons](https://commons.wikimedia.org/wiki/Main_Page)
* **Summaries** – [Wikipedia API](https://www.mediawiki.org/wiki/API:Main_page)

---

## 💡 License

MIT License 
