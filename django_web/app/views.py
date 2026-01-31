from django.shortcuts import render
import requests
from .models import Play

# Create your views here.
def play_game(request, page_id):
    # to get Flask API (Port 5000)
    flask_url=f"http://127.0.0.1:5000/pages/{page_id}"
    response=requests.get(flask_url)

   # converting the response from flask to json
    page_data=response.json()

    if page_data.get('is_ending'):
        Play.objects.create(
            story_id=1, # For now, we assume story 1 (Ford v Ferrari)
            ending_page_id=page_id
        )


    return render(request, 'game/play.html', {'page': page_data})

def home(request):

    reponse=requests.get("http://127.0.0.1:5000/stories")
    stories=reponse.json()
    return render(request, 'game/home.html', {'stories': stories})

