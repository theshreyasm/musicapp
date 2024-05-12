from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/songs', views.songs, name='songs'),
    path('api/playlists', views.playlist, name='playlist'),
    path('api/playlists/<int:playlist_id>', views.playlist, name='change_playlist_name'),
    path('api/playlists/<int:playlist_id>/songs', views.playlist_songs, name='playlist_songs'),
    path('api/playlists/<int:playlist_id>/songs/<int:song_id>', views.playlist_changes, name='move_remove_song'),
]