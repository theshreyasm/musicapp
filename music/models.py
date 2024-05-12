from django.db import models

class Song(models.Model):
    name = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    release_year = models.IntegerField()

    def __str__(self):
        return self.name
    

class Playlist(models.Model):
    name = models.CharField(max_length=100)
    songs = models.JSONField()  # Array of integers (song IDs)
