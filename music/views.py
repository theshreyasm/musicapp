from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.paginator import Paginator
from .models import Song, Playlist
from .serializers import SongSerializer, PlaylistSerializer, PlaylistListSerializer, PlaylistSongSerializer
from urllib.parse import urlencode
from django.shortcuts import render
from django.http import Http404
from django.db.models import Case, When

def home(request):
    return render(request, 'music/home.html')

@api_view(['GET', 'POST'])
def songs(request):
    if request.method == 'GET':
        page_number = int(request.GET.get('page', 1))
        songs = Song.objects.all().order_by('id')

        paginator = Paginator(songs, 10)
        page_obj = paginator.get_page(page_number)

        serializer = SongSerializer(page_obj, many=True)

        next_page_url = None
        if page_obj.has_next():
            next_page_url = request.path + '?' + urlencode({'page': page_obj.next_page_number()})
        previous_page_url = None
        if page_obj.has_previous():
            previous_page_url = request.path + '?' + urlencode({'page': page_obj.previous_page_number()})

        response_data = {
            'count': paginator.count,
            'next': next_page_url,
            'previous': previous_page_url,
            'results': serializer.data
        }

        return Response(response_data)

    elif request.method == 'POST':
        serializer = SongSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def playlist(request, playlist_id=None):
    if request.method == 'GET':
        page_number = int(request.GET.get('page', 1))

        playlists = Playlist.objects.all().order_by('id')

        paginator = Paginator(playlists, 10)
        page_obj = paginator.get_page(page_number)

        serializer = PlaylistListSerializer(page_obj, many=True)

        next_page_url = None
        if page_obj.has_next():
            next_page_url = request.path + '?' + urlencode({'page': page_obj.next_page_number()})
        previous_page_url = None
        if page_obj.has_previous():
            previous_page_url = request.path + '?' + urlencode({'page': page_obj.previous_page_number()})

        response_data = {
            'count': paginator.count,
            'next': next_page_url,
            'previous': previous_page_url,
            'results': serializer.data
        }

        return Response(response_data)
    
    elif request.method == 'POST':
        serializer = PlaylistSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    elif request.method == 'PUT':
        try:
            playlist = Playlist.objects.get(pk=playlist_id)
        except Playlist.DoesNotExist:
            raise Http404("Playlist does not exist.")
        
        serializer = PlaylistListSerializer(playlist, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    elif request.method == 'DELETE':
        try:
            playlist = Playlist.objects.get(pk=playlist_id)
        except Playlist.DoesNotExist:
            raise Http404("Playlist does not exist")

        playlist.delete()
        return Response(status=200)

@api_view(['GET'])   
def playlist_songs(request, playlist_id):
    try:
        playlist = Playlist.objects.get(pk=playlist_id)
    except Playlist.DoesNotExist:
        raise Http404("Playlist does not exist.")

    page_number = int(request.GET.get('page', 1))

    song_ids = playlist.songs
    ordering_cases = [When(id=id_val, then=pos) for pos, id_val in enumerate(song_ids)]
    songs = Song.objects.filter(id__in=song_ids).order_by(Case(*ordering_cases, default=0))

    page_size = 10
    paginator = Paginator(songs, page_size)
    page_obj = paginator.get_page(page_number)

    serializer = PlaylistSongSerializer(page_obj, many=True, context={'request': request, 'page_size': page_size})

    next_page_url = None
    if page_obj.has_next():
        next_page_url = request.path + '?' + urlencode({'page': page_obj.next_page_number()})
    previous_page_url = None
    if page_obj.has_previous():
        previous_page_url = request.path + '?' + urlencode({'page': page_obj.previous_page_number()})

    response_data = {
        'count': paginator.count,
        'next': next_page_url,
        'previous': previous_page_url,
        'results': serializer.data
    }

    return Response(response_data)


@api_view(['PUT', 'DELETE'])
def playlist_changes(request, playlist_id, song_id):
    if request.method == 'PUT':
        try:
            playlist = Playlist.objects.get(pk=playlist_id)
        except Playlist.DoesNotExist:
            raise Http404("Playlist does not exist.")

        song_ids = playlist.songs
        if song_id not in song_ids:
            raise Http404("Song does not exist in the playlist.")

        index = song_ids.index(song_id)
        position = request.data.get('position') - 1

        song_ids.remove(song_id)
        song_ids.insert(position, song_id)

        playlist.songs = song_ids
        playlist.save()

        return Response(status=200)
    
    elif request.method == 'DELETE':
        try:
            playlist = Playlist.objects.get(pk=playlist_id)
        except Playlist.DoesNotExist:
            raise Http404("Playlist does not exist.")

        song_ids = playlist.songs
        if song_id not in song_ids:
            raise Http404("Song does not exist in the playlist.")

        song_ids.remove(song_id)
        playlist.songs = song_ids
        playlist.save()

        return Response(status=200)


