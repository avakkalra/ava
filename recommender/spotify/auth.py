import base64
import requests
from urllib.parse import urlencode
from django.conf import settings


def get_spotify_auth_url():
    """
    Generate the Spotify authorization URL for OAuth flow.
    """
    scope = " ".join([
        "user-read-private",
        "user-read-email",
        "user-library-read",
        "playlist-modify-public",
        "playlist-modify-private",
    ])
    
    params = {
        'client_id': settings.SPOTIFY_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': settings.SPOTIFY_REDIRECT_URI,
        'scope': scope,
        'show_dialog': 'true'
    }
    
    auth_url = f"https://accounts.spotify.com/authorize?{urlencode(params)}"
    return auth_url


def get_spotify_tokens(code):
    """
    Exchange authorization code for access and refresh tokens.
    """
    auth_header = base64.b64encode(
        f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}".encode()
    ).decode('ascii')
    
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': settings.SPOTIFY_REDIRECT_URI
    }
    
    response = requests.post(
        'https://accounts.spotify.com/api/token',
        headers=headers,
        data=data
    )
    
    return response.json() if response.status_code == 200 else None


def refresh_access_token(refresh_token):
    """
    Refresh the access token using a refresh token.
    """
    auth_header = base64.b64encode(
        f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}".encode()
    ).decode('ascii')
    
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    
    response = requests.post(
        'https://accounts.spotify.com/api/token',
        headers=headers,
        data=data
    )
    
    return response.json() if response.status_code == 200 else None