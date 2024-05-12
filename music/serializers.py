from rest_framework import serializers
from .models import Song, Playlist
from django.db import transaction

class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ['id', 'name', 'artist', 'release_year']


class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = ['id', 'name', 'songs']

    def validate_songs(self, value):
        # Check if all song IDs exist in the Song table
        song_ids = Song.objects.values_list('id', flat=True)
        invalid_ids = [song_id for song_id in value if song_id not in song_ids]
        if invalid_ids:
            raise serializers.ValidationError(f"Invalid song IDs: {', '.join(map(str, invalid_ids))}")
        return value


class PlaylistListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = ['id', 'name']


class PlaylistSongSerializer(serializers.ModelSerializer):
    position = serializers.SerializerMethodField()

    class Meta:
        model = Song
        fields = ['id', 'name', 'artist', 'release_year', 'position']

    def get_position(self, obj):
        queryset = self.instance
        page_number = self.context['request'].query_params.get('page', 1)
        page_size = self.context.get('page_size', 10)
        start_position = (int(page_number) - 1) * int(page_size) + 1
        position = list(queryset).index(obj) + start_position
        return position