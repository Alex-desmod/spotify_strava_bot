import os
import logging

from dotenv import load_dotenv

from web_server.config import SPOTIFY_REDIRECT_URI

load_dotenv()

MAIN_ENDPOINT = "https://api.spotify.com/v1/me"
AUTH_URL = "https://accounts.spotify.com/authorize"
SCOPES = "user-top-read user-read-recently-played user-read-private"

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")

logger = logging.getLogger(__name__)


def get_auth_link(tg_id):
    return (f"{AUTH_URL}?client_id={SPOTIFY_CLIENT_ID}&response_type=code&redirect_uri={SPOTIFY_REDIRECT_URI}"
            f"&state={tg_id}&scope={SCOPES}")

def get_tops_link(entity, time_range, limit):
    return f"{MAIN_ENDPOINT}/top/{entity}?time_range={time_range}&limit={limit}&offset=0"