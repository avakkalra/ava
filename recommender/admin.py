from django.contrib import admin
from .models import UserProfile, RecommendationHistory

admin.site.register(UserProfile)
admin.site.register(RecommendationHistory)