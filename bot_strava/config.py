import os
import logging

from dotenv import load_dotenv

from web_server.config import STRAVA_REDIRECT_URI

load_dotenv()

STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
AUTH_URL = "https://www.strava.com/oauth/authorize"
SCOPES = "read,activity:read"


def get_auth_link(tg_id):
    return (f"{AUTH_URL}?client_id={STRAVA_CLIENT_ID}&response_type=code&redirect_uri={STRAVA_REDIRECT_URI}"
            f"&state={tg_id}&scope={SCOPES}")