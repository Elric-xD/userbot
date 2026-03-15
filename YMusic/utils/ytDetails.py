import requests
from pytubefix import Search, YouTube as pyYouTube, Playlist
from urllib.parse import urlparse, parse_qs

API_URL = "https://yt-api-vercelgg-six.vercel.app/"


def searchYt(query, is_videoId=False):
    query = str(query)
    if is_videoId:
        video = pyYouTube(f"https://www.youtube.com/watch?v={query}")
        title = video.title
        duration = video.length
        link = video.watch_url
        return title, duration, link
    else:
        videosResult = Search(query)
        for Result in videosResult.videos:
            title = Result.title
            duration = Result.length
            link = Result.watch_url
            return title, duration, link
    return None, None, None


def search_api(query, is_videoId=False, video=False):
    query = str(query)
    if is_videoId:
        response = requests.get(
            f"{API_URL}download/{'ytmp4' if video else 'ytmp3'}?url=https://youtube.com/watch?v=" + query
        )
        data = response.json()
        if data["success"]:
            title = data["result"]["title"]
            duration = "Unknown"
            link = data["result"]["download_url"]
            return title, duration, link
    else:
        response = requests.get(f"{API_URL}song?query=" + query)
        data = response.json()
        if data["status"]:
            result = data["result"]
            if result:
                title = result["title"]
                duration = result["duration"]
                link = (
                    result["video"]["download_url"]
                    if video
                    else result["audio"]["download_url"]
                )
                return title, duration, link
    return None, None, None


def searchPlaylist(query):
    query = str(query)
    playlistResult = Playlist(query)
    title = playlistResult.title
    duration = playlistResult.length
    return title, duration


def extract_playlist_id(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    playlist_id = query_params.get("list", [None])[0]
    return playlist_id


def extract_video_id(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname == "youtu.be":
        video_id = parsed_url.path[1:]
    else:
        query_params = parse_qs(parsed_url.query)
        video_id = query_params.get("v", [None])[0]
    return video_id
