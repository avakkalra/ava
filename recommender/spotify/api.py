import requests
import random


def get_user_profile(access_token):
    """
    Get the user's Spotify profile information.
    """
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    response = requests.get(
        'https://api.spotify.com/v1/me',
        headers=headers
    )
    
    return response.json() if response.status_code == 200 else None


def get_user_library(access_token, limit=50):
    """
    Get tracks from the user's Spotify library.
    """
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    tracks = []
    offset = 0
    total = None
    
    # Spotify API allows a maximum of 50 items per request
    # We'll paginate to get more items
    while total is None or offset < total:
        response = requests.get(
            f'https://api.spotify.com/v1/me/tracks?limit={limit}&offset={offset}',
            headers=headers
        )
        
        if response.status_code != 200:
            break
        
        data = response.json()
        total = data['total']
        
        # Process each saved track
        for item in data['items']:
            track = item['track']
            
            # Extract relevant track information
            track_info = {
                'id': track['id'],
                'name': track['name'],
                'uri': track['uri'],
                'artists': [{'id': artist['id'], 'name': artist['name']} for artist in track['artists']],
                'album': {
                    'id': track['album']['id'],
                    'name': track['album']['name'],
                    'release_date': track['album']['release_date']
                },
                'popularity': track['popularity'],
                'preview_url': track['preview_url'],
                'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None
            }
            
            tracks.append(track_info)
        
        offset += limit
        
        # In a real app, we'd implement rate limiting and delay here
        
        # For demo purposes, limit to 100 tracks total
        if offset >= 1000:
            break
    
    return tracks

def create_spotify_playlist(access_token, user_id, name, description=""):
    """
    Create a new playlist on Spotify.
    """
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'name': name,
        'description': description,
        'public': True
    }
    
    response = requests.post(
        f'https://api.spotify.com/v1/users/{user_id}/playlists',
        headers=headers,
        json=data
    )
    
    return response.json() if response.status_code in [200, 201] else None


import requests
import urllib.parse

def search_playlist_by_mood(access_token, mood, max_results=10):
    """
    Search for playlists by mood on Spotify.
    """
    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    params = {
        'q': mood,
        'type': 'playlist',
        'limit': max_results
    }

    response = requests.get(
        'https://api.spotify.com/v1/search',
        headers=headers,
        params=params
    )

    if response.status_code == 200:
        items = response.json()
        items = items.get('playlists', {}).get('items', [])
        items = list(filter(lambda x: x, items))
        return random.choice(items).get('id', None) if items else None
         
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def get_tracks_from_playlist(access_token, playlist_id, max_tracks=10):
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    params = {
        'limit': max_tracks
    }
    response = requests.get(
        f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks',
        headers=headers,
        params=params
    )
    if response.status_code == 200:
        return response.json().get('items', [])
    else:
        print("Error getting tracks:", response.status_code, response.text)
        return []    
    
def add_tracks_to_playlist(access_token, playlist_id, track_uris):
    """
    Add tracks to a Spotify playlist.
    """
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Spotify API has a limit of 100 tracks per request
    max_tracks_per_request = 100
    
    for i in range(0, len(track_uris), max_tracks_per_request):
        chunk = track_uris[i:i + max_tracks_per_request]
        
        data = {
            'uris': chunk
        }
        
        response = requests.post(
            f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks',
            headers=headers,
            json=data
        )
        
        if response.status_code not in [200, 201]:
            return None
    
    return response.json() if response.status_code in [200, 201] else None