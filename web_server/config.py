import os

from dotenv import load_dotenv

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_REDIRECT_URI = "https://radiogaga.site/callback/spotify"

STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"
STRAVA_REDIRECT_URI = "https://radiogaga.site/callback/strava"
STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")