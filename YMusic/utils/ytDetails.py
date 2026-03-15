import requests
from urllib.parse import urlparse, parse_qs

# Your updated Vercel URL
API_URL = "https://yt-api-vercelgg-six.vercel.app/"

def search_api(query, is_videoId=False, video=False):
    """
    Uses your Vercel API to find a song/video and return a direct download/stream link.
    """
    query = str(query)
    
    # 1. Determine the endpoint and parameters
    if is_videoId:
        # If it's a video ID, we use the URL parameter
        target_url = f"https://www.youtube.com/watch?v={query}"
        endpoint = f"{API_URL}api/all?url={target_url}"
    else:
        # Otherwise, we use the search parameter
        endpoint = f"{API_URL}api/all?search={query}"

    try:
        response = requests.get(endpoint)
        data = response.json()

        # Check if the API returned an error
        if "error" in data:
            print(f"API Error: {data['error']}")
            return None, None, None

        title = data.get("title")
        duration = data.get("duration") # This will be in seconds from /api/all
        
        # 2. Select the correct link (Audio or Video)
        formats = data.get("formats", [])
        
        if video:
            # Filter for video-only or progressive (video+audio)
            video_links = [f for f in formats if f['kind'] in ('video-only', 'progressive')]
            # Sort by height to get best quality, then pick the first
            video_links.sort(key=lambda x: x.get('height', 0), reverse=True)
            link = video_links[0]['url'] if video_links else None
        else:
            # Filter for audio-only or progressive
            audio_links = [f for f in formats if f['kind'] in ('audio-only', 'progressive')]
            # Sort by bitrate (abr) to get best quality
            audio_links.sort(key=lambda x: x.get('abr', 0), reverse=True)
            link = audio_links[0]['url'] if audio_links else None

        return title, duration, link

    except Exception as e:
        print(f"Request failed: {e}")
        return None, None, None

def searchPlaylist(url):
    """
    Uses your /api/playlist endpoint
    """
    try:
        endpoint = f"{API_URL}api/playlist?url={url}"
        response = requests.get(endpoint)
        data = response.json()
        
        title = data.get("title")
        count = data.get("item_count")
        return title, count
    except:
        return None, None

# --- Utility Functions remain the same ---

def extract_playlist_id(url):
    query_params = parse_qs(urlparse(url).query)
    return query_params.get("list", [None])[0]

def extract_video_id(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname == "youtu.be":
        return parsed_url.path[1:]
    return parse_qs(parsed_url.query).get("v", [None])[0]
            
