import requests
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import Play

# --- LEVEL 13: HOME WITH SEARCH & STATS ---
def home(request):
    query = request.GET.get('search', '')
    
    # Fetch stories from Flask API
    try:
        response = requests.get("http://127.0.0.1:5000/stories")
        stories = response.json() if response.status_code == 200 else []
    except:
        stories = []

    # Level 13: Path Statistics (Counting plays from Django DB)
    play_stats = Play.objects.values('story_id').annotate(total=Count('id'))
    stats_dict = {item['story_id']: item['total'] for item in play_stats}

    for story in stories:
        story['play_count'] = stats_dict.get(story['id'], 0)

    # Search filter
    if query:
        stories = [s for s in stories if query.lower() in s['title'].lower()]

    return render(request, 'game/home.html', {'stories': stories, 'query': query})

# --- LEVEL 16: REGISTRATION ---
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# --- LEVEL 16: PLAY GAME (The function your error is looking for!) ---
@login_required
def play_game(request, story_id):
    try:
        # Ask Flask where the story starts
        response = requests.get(f"http://127.0.0.1:5000/stories/{story_id}/start")
        data = response.json()
        start_page_id = data.get('start_page_id')
        
        # In a real race, we'd redirect to the first page
        # For now, let's just render the play template
        return render(request, 'game/play.html', {'page_id': start_page_id, 'story_id': story_id})
    except:
        return redirect('home')