import os
import logging

from dotenv import load_dotenv

from web_server.config import STRAVA_REDIRECT_URI

load_dotenv()

STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
AUTH_URL = "https://www.strava.com/oauth/authorize"