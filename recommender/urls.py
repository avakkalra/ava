from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('connect-spotify/', views.connect_spotify, name='connect_spotify'),
    path('callback/', views.spotify_callback, name='spotify_callback'),
    path('recommend/', views.recommend, name='recommend'),
    path('history/', views.history, name='history'),
    path('create-playlist/<int:history_id>/', views.create_playlist, name='create_playlist'),
]