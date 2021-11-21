from django.shortcuts import render, redirect

# Create your views here.
from django.shortcuts import render, redirect
from django.http import Http404

def index(request):
    if request.method == "POST":
        room_code = request.POST.get("room_code")
        char_choice = request.POST.get("character_choice")
        return redirect(
            '/play/%s?&choice=%s'
            % (room_code, char_choice)
        )
    return render(request, "index.html", {})


def game(request, room_code):

    context = {
        "room_code": room_code
    }
    return render(request, "game.html", context)


def show_img(request):

    context = {

    }
    return render(request, "image.html", context)