from django.db import models
from django.contrib.auth.models import User
import json


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    spotify_id = models.CharField(max_length=255, blank=True, null=True)
    access_token = models.TextField(blank=True, null=True)
    refresh_token = models.TextField(blank=True, null=True)
    token_expires_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"


class RecommendationHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prompt = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    tracks = models.TextField()  # JSON string of recommended tracks
    
    def __str__(self):
        return f"{self.user.username} - {self.prompt} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    def get_tracks(self):
        return json.loads(self.tracks)
    
    def set_tracks(self, tracks_list):
        self.tracks = json.dumps(tracks_list)