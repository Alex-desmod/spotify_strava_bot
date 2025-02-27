import os
import httpx
import logging

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select

from web_server.config import (SPOTIFY_TOKEN_URL, SPOTIFY_REDIRECT_URI, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET,
                               STRAVA_TOKEN_URL, STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET)
from web_server.database import get_spotify_session, get_strava_session
from bot_spotify.models import User as SpotifyUser
from bot_strava.models import User as StravaUser

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

app.mount("/static", StaticFiles(directory="web_server/static"), name="static")

@app.get("/callback/spotify")
async def callback_spotify(request: Request):
    """Handling the Spotify redirect after autorization."""
    code = request.query_params.get("code")
    tg_id = request.query_params.get("state")

    if not code:
        return {"error": "Authorization failed"}

    # Changing the code for access_token
    async with httpx.AsyncClient() as client:
        response = await client.post(url=SPOTIFY_TOKEN_URL,
                                        data={
                                            "grant_type": "authorization_code",
                                            "code": code,
                                            "redirect_uri": SPOTIFY_REDIRECT_URI,
                                            "client_id": SPOTIFY_CLIENT_ID,
                                            "client_secret": SPOTIFY_CLIENT_SECRET,
                                        },
                                        headers={"Content-Type": "application/x-www-form-urlencoded"}
                                        )
        token_data = response.json()

    # Check if we got the access_token
    if "access_token" in token_data:
        access_token = token_data["access_token"]
        refresh_token = token_data["refresh_token"]
        async for session in get_spotify_session():
            user = await session.scalar(select(SpotifyUser).where(SpotifyUser.tg_id == tg_id))
            if user:
                user.access_token = access_token
                user.refresh_token = refresh_token
            else:
                session.add(SpotifyUser(tg_id=tg_id, access_token=access_token, refresh_token=refresh_token))
            await session.commit()

        return templates.TemplateResponse("callback_spotify.html", {"request": request})
    else:
        return {"error": "Failed to get access token"}


@app.get("/callback/strava")
async def callback_strava(request: Request):
    """Handling the Strava redirect after autorization."""
    code = request.query_params.get("code")
    tg_id = request.query_params.get("state")

    if not code:
        return {"error": "Authorization failed"}

    # Changing the code for access_token
    async with httpx.AsyncClient() as client:
        response = await client.post(url=STRAVA_TOKEN_URL,
                                        data={
                                            "grant_type": "authorization_code",
                                            "code": code,
                                            "client_id": STRAVA_CLIENT_ID,
                                            "client_secret": STRAVA_CLIENT_SECRET,
                                        })
        token_data = response.json()

    # Check if we got the access_token
    if "access_token" in token_data:
        access_token = token_data["access_token"]
        refresh_token = token_data["refresh_token"]
        expires_at = token_data["expires_at"]
        athlete_id = token_data["athlete"]["id"]
        async for session in get_strava_session():
            user = await session.scalar(select(StravaUser).where(StravaUser.tg_id == tg_id))
            if user:
                user.access_token = access_token
                user.refresh_token = refresh_token
                user.expires_at = expires_at
                user.athlete_id = athlete_id
            else:
                session.add(StravaUser(tg_id=tg_id,
                                       access_token=access_token,
                                       refresh_token=refresh_token,
                                       expires_at=expires_at,
                                       athlete_id=athlete_id))
            await session.commit()

        return templates.TemplateResponse("callback_strava.html", {"request": request})
    else:
        return {"error": "Failed to get access token"}

