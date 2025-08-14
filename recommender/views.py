from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.http import JsonResponse
from datetime import timedelta
import json
import uuid
from .recommendation.engine import MoodMusicRecommender
from .models import UserProfile, RecommendationHistory
from .spotify.auth import get_spotify_auth_url, get_spotify_tokens
from .spotify.api import (
    get_user_profile, 
    get_user_library, 
    create_spotify_playlist,
    add_tracks_to_playlist,
    search_playlist_by_mood,
    get_tracks_from_playlist
)


def home(request):
    print("Hello world", flush=True)
    """Home page view."""
    return render(request, 'recommender/home.html')


def login_view(request):
    """Login view with Spotify."""
    # if request.method == 'POST':
    #     auth_url = get_spotify_auth_url()
    #     # Create a temporary user for Spotify auth flow
    return redirect('connect_spotify')
    # return render(request, 'recommender/login.html')


@login_required
def logout_view(request):
    """Logout view."""
    logout(request)
    return redirect('home')


def connect_spotify(request):
    """Connect to Spotify."""
    auth_url = get_spotify_auth_url()
    return redirect(auth_url)


def spotify_callback(request):
    """Handle Spotify OAuth callback."""
    code = request.GET.get('code')
    
    if not code:
        messages.error(request, "Authorization failed. Please try again.")
        return redirect('home')
    
    # Get tokens from Spotify
    token_data = get_spotify_tokens(code)
    
    if not token_data or 'error' in token_data:
        messages.error(request, "Failed to connect to Spotify. Please try again.")
        return redirect('home')
    
    # Get Spotify user profile
    access_token = token_data['access_token']
    refresh_token = token_data['refresh_token']
    expires_in = token_data['expires_in']
    
    spotify_profile = get_user_profile(access_token)
    
    if not spotify_profile or 'error' in spotify_profile:
        messages.error(request, "Failed to get Spotify profile. Please try again.")
        return redirect('home')
    
    # Update user profile
    user, created = User.objects.get_or_create(username=spotify_profile['id'])
    if created:
        user.username = spotify_profile['display_name'] or f"user_{spotify_profile['id']}"
        user.save()
    
    # Create or update UserProfile
    token_expires_at = timezone.now() + timedelta(seconds=expires_in)
    
    user_profile, created = UserProfile.objects.get_or_create(user=user)
    user_profile.spotify_id = spotify_profile['id']
    user_profile.access_token = access_token
    user_profile.refresh_token = refresh_token
    user_profile.token_expires_at = token_expires_at
    user_profile.save()

    request.user = user
    request._cached_user = user  # Update the request user
    login(request, user)
    
    messages.success(request, "Successfully connected to Spotify!")
    return redirect('home')


@login_required
def recommend(request):
    """Generate recommendations based on prompt."""
    if request.method == 'POST':
        prompt = request.POST.get('prompt', '').strip()
        
        if not prompt:
            messages.error(request, "Please enter a prompt.")
            return redirect('recommend')
        
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            
            # Check if token is expired and refresh if needed
            if user_profile.token_expires_at and user_profile.token_expires_at <= timezone.now():
                # In a real app, we would refresh the token here
                messages.error(request, "Spotify session expired. Please reconnect.")
                return redirect('connect_spotify')
            
            # Get user library from Spotify
            # library = get_user_library(user_profile.access_token)
            playlist_id = search_playlist_by_mood(user_profile.access_token, prompt)
            tracks = get_tracks_from_playlist(user_profile.access_token, playlist_id)
            
            # Save recommendation to history
            history = RecommendationHistory(
                user=request.user,
                prompt=prompt
            )
            history.set_tracks(tracks)
            history.save()
            
            return render(request, 'recommender/recommendations.html', {
                'prompt': prompt,
                'tracks': tracks,
                'history_id': history.id
            })
        
        except UserProfile.DoesNotExist:
            messages.error(request, "Please connect your Spotify account first.")
            return redirect('connect_spotify')
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('home')
    
    return render(request, 'recommender/recommend_form.html')


@login_required
def history(request):
    """Show recommendation history."""
    try:
        histories = RecommendationHistory.objects.filter(user=request.user).order_by('-created_at')
        
        for history in histories:
            history.tracks_list = history.get_tracks()
        
        return render(request, 'recommender/history.html', {'histories': histories})
    
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('home')


@login_required
def create_playlist(request, history_id):
    """Create a Spotify playlist from recommendations."""
    try:
        history = RecommendationHistory.objects.get(id=history_id, user=request.user)
        tracks = history.get_tracks()
        user_profile = UserProfile.objects.get(user=request.user)
        
        # Create playlist on Spotify
        playlist_name = f"Recommended: {history.prompt}"
        playlist = create_spotify_playlist(
            user_profile.access_token,
            user_profile.spotify_id,
            playlist_name,
            f"Songs recommended for prompt: {history.prompt}"
        )
        
        if 'id' in playlist:
            # Add tracks to playlist
            track_uris = [track['uri'] for track in tracks]
            result = add_tracks_to_playlist(user_profile.access_token, playlist['id'], track_uris)
            
            if 'snapshot_id' in result:
                messages.success(request, "Playlist created successfully!")
                return redirect('history')
        
        messages.error(request, "Failed to create playlist. Please try again.")
        
    except RecommendationHistory.DoesNotExist:
        messages.error(request, "Recommendation not found.")
    except UserProfile.DoesNotExist:
        messages.error(request, "Please connect your Spotify account first.")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
    
    return redirect('history')