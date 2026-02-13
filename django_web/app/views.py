import requests
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg 
from .models import Play, StoryRating, StoryReport

# for Docker service 
FLASK_BASE_URL = "http://flask_api:5000"

def home(request):
    query = request.GET.get('search', '')
    stories = []
    
    try:
        # Fetching raw race data from the Flask container
        response = requests.get(f"{FLASK_BASE_URL}/stories", timeout=5)
        if response.status_code == 200:
            stories = response.json()
    except Exception as e:
        print(f"Flask Connection Error: {e}")
        stories = []

    # Get local Django DB statistics (Play counts)
    play_stats = Play.objects.values('story_id').annotate(total=Count('id'))
    stats_dict = {item['story_id']: item['total'] for item in play_stats}

    # Get local Django DB statistics (Ratings)
    rating_stats = StoryRating.objects.values('story_id').annotate(
        avg_stars=Avg('stars'), 
        rating_count=Count('id')
    )
    ratings_dict = {item['story_id']: item for item in rating_stats}

    # Injecting local Django stats into the Flask API data
    for story in stories:
        story['play_count'] = stats_dict.get(story['id'], 0)
        r_data = ratings_dict.get(story['id'], {'avg_stars': 0, 'rating_count': 0})
        story['avg_rating'] = round(r_data['avg_stars'], 1) if r_data['avg_stars'] else 0
        story['rating_count'] = r_data['rating_count']

    # Filter stories based on the search input
    if query:
        stories = [s for s in stories if query.lower() in s['title'].lower()]

    return render(request, 'game/home.html', {'stories': stories, 'query': query})

@login_required 
def play_game(request, story_id, page_id=None):
    try:
        if not page_id:
            res = requests.get(f"{FLASK_BASE_URL}/stories/{story_id}/start")
            page_id = res.json().get('start_page_id')

        response = requests.get(f"{FLASK_BASE_URL}/pages/{page_id}")
        page_data = response.json()

        if page_data.get('is_ending'):
            Play.objects.create(
                user=request.user,
                story_id=story_id,
                ending_label=page_data.get('ending_label', 'Finish')
            )

        return render(request, 'game/play.html', {
            'page': page_data, 
            'story_id': story_id
        })
    except Exception as e:
        print(f"Play Error: {e}")
        return redirect('home')

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



@login_required
def submit_rating(request, story_id):
    if request.method == 'POST':
        stars = request.POST.get('stars')
        comment = request.POST.get('comment')
        StoryRating.objects.update_or_create(
            user=request.user,
            story_id=story_id,
            defaults={'stars': stars, 'comment': comment}
        )
    return redirect('home')

@login_required
def report_story(request, story_id):
    if request.method == 'POST':
        reason = request.POST.get('reason')
        description = request.POST.get('description')
        StoryReport.objects.create(
            user=request.user,
            story_id=story_id,
            reason=reason,
            description=description
        )
        return render(request, 'game/report_success.html')
    return render(request, 'game/report_form.html', {'story_id': story_id})

def story_reviews(request, story_id):
    try:
        response = requests.get(f"{FLASK_BASE_URL}/stories")
        stories = response.json()
        story = next((s for s in stories if s['id'] == story_id), None)
    except:
        story = {'title': 'Race Track'}

    reviews = StoryRating.objects.filter(story_id=story_id).select_related('user').order_by('-created_at')
    return render(request, 'game/story_reviews.html', {
        'story': story,
        'reviews': reviews
    })

@login_required
def create_race(request):
    if request.method == "POST":
        # 1. Grab data from your HTML form
        title = request.POST.get('title')
        description = request.POST.get('description')
        scenario_text = request.POST.get('scenario_text')
        choice_text = request.POST.get('choice_text')

        try:
            # STEP A: Create the Story
            s_res = requests.post(f"{FLASK_BASE_URL}/stories", json={
                "title": title, "description": description
            })
            story_id = s_res.json().get('id')

            # STEP B: Create the First Page
            p_res = requests.post(f"{FLASK_BASE_URL}/stories/{story_id}/pages", json={
                "text": scenario_text, "is_ending": False
            })
            page_id = p_res.json().get('id')

            # STEP C: Create the First Choice
            requests.post(f"{FLASK_BASE_URL}/pages/{page_id}/choices", json={
                "text": choice_text, "next_page_id": None
            })

            # STEP D: THE FIX - Link the start_page_id to the story
            # This makes the URL path('play/<int:story_id>/', ...) work!
            requests.put(f"{FLASK_BASE_URL}/stories/{story_id}", json={
                "start_page_id": page_id
            })

            # 2. Redirect to home page
            return redirect('home')
            
        except Exception as e:
            print(f"Launch Error: {e}")
            return render(request, 'game/create_story.html', {'error': 'API Connection Error'})

    return render(request, 'game/create_story.html')




@login_required
def add_page_view(request, story_id):
    if request.method == "POST":
        page_data = {
            "text": request.POST.get('text'),
            "is_ending": request.POST.get('is_ending') == 'on',
            "ending_label": request.POST.get('ending_label', '')
        }
        
        # Send to Flask API
        response = requests.post(f"{FLASK_BASE_URL}/stories/{story_id}/pages", json=page_data)
        
        if response.status_code == 201:
            return redirect('home') # For now, go home. Later, you can redirect to add more choices.

    return render(request, 'game/create_story.html', {'story_id': story_id})


@login_required
def add_choice_view(request, story_id, page_id):
    if request.method == "POST":
        choice_data = {
            "text": request.POST.get('text'),
            "next_page_id": request.POST.get('next_page_id')
        }
        
        # POST to Flask
        response = requests.post(f"{FLASK_BASE_URL}/pages/{page_id}/choices", json=choice_data)
        
        if response.status_code == 201:
            # Take them back to the story creation hub or the current page
            return redirect('create_page', story_id=story_id)

    return render(request, 'game/create_story.html', {
        'story_id': story_id,
        'page_id': page_id
    })





@login_required
def delete_race(request, story_id):
    # Only allow POST or a specific delete action for security
    try:
        response = requests.delete(f"{FLASK_BASE_URL}/stories/{story_id}")
        if response.status_code == 200:
            # Also delete local Django stats if you want to clean up totally
            Play.objects.filter(story_id=story_id).delete()
            StoryRating.objects.filter(story_id=story_id).delete()
            
    except Exception as e:
        print(f"Delete Error: {e}")
        
    return redirect('home')







