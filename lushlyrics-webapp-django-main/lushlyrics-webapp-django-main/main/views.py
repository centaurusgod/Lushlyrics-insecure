from django.db import IntegrityError
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import playlist_user
from django.urls.base import reverse
from django.contrib.auth import authenticate, login, logout
from youtube_search import YoutubeSearch
import json

# import cardupdate


f = open("card.json", "r")
CONTAINER = json.load(f)


def default(request):
    global CONTAINER

    if request.method == "POST":

        add_playlist(request)
        return HttpResponse("")

    song = "kSFJGEHDCrQ"
    return render(request, "player.html", {"CONTAINER": CONTAINER, "song": song})


def user_login_handler(request):
    if request.method == "GET":
        return render(request, "login.html")
    elif request.method == "POST":
        return render(
            request,
        )


def user_registration_handler(request):
    if request.method == "GET":
        return render(request, "signup.html")
    elif request.method == "POST":
        # Retrieve form data
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm-password")

        if password != confirm_password:
            print("Error: Passwords don't match")
            return render(request, "signup.html")

        username_exists = User.objects.filter(username=username).exists()
        email_exists = User.objects.filter(email=email).exists()

        try:
            if username_exists and email_exists:
                return render(
                    request, "signup.html", {"username": username, "email": email}
                )
            if username_exists:
                return render(
                    request, "signup.html", {"username": username}
                )
            if email_exists:
                return render(request, "signup.html", {"email":email})

            user = User.objects.create_user(username, email, password)
            user.save()
            return render(request, "login.html")
        except IntegrityError as e:
            print("Error:", e)
            return render(request, "signup.html", {"username": username})

        finally:
            print("Do somethng")


def playlist(request):
    cur_user = playlist_user.objects.get(username=request.user)
    try:
        song = request.GET.get("song")
        song = cur_user.playlist_song_set.get(song_title=song)
        song.delete()
    except:
        pass
    if request.method == "POST":
        add_playlist(request)
        return HttpResponse("")
    song = "kSFJGEHDCrQ"
    user_playlist = cur_user.playlist_song_set.all()
    # print(list(playlist_row)[0].song_title)
    return render(
        request, "playlist.html", {"song": song, "user_playlist": user_playlist}
    )


def search(request):
    if request.method == "POST":

        add_playlist(request)
        return HttpResponse("")
    try:
        search = request.GET.get("search")
        song = YoutubeSearch(search, max_results=10).to_dict()
        song_li = [song[:10:2], song[1:10:2]]
        # print(song_li)
    except:
        return redirect("/")

    return render(
        request, "search.html", {"CONTAINER": song_li, "song": song_li[0][0]["id"]}
    )


def add_playlist(request):
    cur_user = playlist_user.objects.get(username=request.user)

    if (request.POST["title"],) not in cur_user.playlist_song_set.values_list(
        "song_title",
    ):

        songdic = (YoutubeSearch(request.POST["title"], max_results=1).to_dict())[0]
        song__albumsrc = songdic["thumbnails"][0]
        cur_user.playlist_song_set.create(
            song_title=request.POST["title"],
            song_dur=request.POST["duration"],
            song_albumsrc=song__albumsrc,
            song_channel=request.POST["channel"],
            song_date_added=request.POST["date"],
            song_youtube_id=request.POST["songid"],
        )
