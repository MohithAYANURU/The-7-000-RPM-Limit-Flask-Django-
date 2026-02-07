import requests
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg 
from .models import Play, StoryRating

def home(request):
    query = request.GET.get('search', '')
    try:
        response = requests.get("http://127.0.0.1:5000/stories")
        stories = response.json() if response.status_code == 200 else []
    except:
        stories = []

    # Level 13: Path Statistics
    play_stats = Play.objects.values('story_id').annotate(total=Count('id'))
    stats_dict = {item['story_id']: item['total'] for item in play_stats}

    # --- ADD THIS: Level 18-20 Rating Stats ---
    rating_stats = StoryRating.objects.values('story_id').annotate(
        avg_stars=Avg('stars'), 
        rating_count=Count('id')
    )
    ratings_dict = {item['story_id']: item for item in rating_stats}
    # ------------------------------------------

    for story in stories:
        # Merge Play Counts
        story['play_count'] = stats_dict.get(story['id'], 0)
        
        # Merge Rating Data
        r_data = ratings_dict.get(story['id'], {'avg_stars': 0, 'rating_count': 0})
        story['avg_rating'] = round(r_data['avg_stars'], 1) if r_data['avg_stars'] else 0
        story['rating_count'] = r_data['rating_count']

    if query:
        stories = [s for s in stories if query.lower() in s['title'].lower()]

    return render(request, 'game/home.html', {'stories': stories, 'query': query})
@login_required # Level 16: Security
def play_game(request, story_id, page_id=None):
    try:
        # If entering for the first time
        if not page_id:
            res = requests.get(f"http://127.0.0.1:5000/stories/{story_id}/start")
            page_id = res.json().get('start_page_id')

        # Fetch page content
        response = requests.get(f"http://127.0.0.1:5000/pages/{page_id}")
        page_data = response.json()

        # Level 13/16: Record the finish
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
        print(f"Error: {e}")
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



# --- LEVEL 18-20: ADVANCED FEATURES ---

def story_map(request, story_id):
    """Fulfills the Quality Requirement: Story tree visualization"""
    try:
        # Fetch the story title from Flask
        res = requests.get(f"http://127.0.0.1:5000/stories")
        stories = res.json()
        story_name = next((s['title'] for s in stories if s['id'] == story_id), "Race Track")
        
        return render(request, 'game/visualize.html', {
            'story_id': story_id,
            'story_title': story_name
        })
    except:
        return redirect('home')

@login_required
def submit_rating(request, story_id):
    """Authenticated users can rate 1-5 stars + comment"""
    if request.method == 'POST':
        stars = request.POST.get('stars')
        comment = request.POST.get('comment')
        
        from .models import StoryRating
        StoryRating.objects.update_or_create(
            user=request.user,
            story_id=story_id,
            defaults={'stars': stars, 'comment': comment}
        )
    return redirect('home')

@login_required
def report_story(request, story_id):
    """Users can report a story with a reason"""
    if request.method == 'POST':
        reason = request.POST.get('reason')
        description = request.POST.get('description')
        
        from .models import StoryReport
        StoryReport.objects.create(
            user=request.user,
            story_id=story_id,
            reason=reason,
            description=description
        )
        return render(request, 'game/report_success.html') # Create a simple 'Thank you' page
    
    return render(request, 'game/report_form.html', {'story_id': story_id})



    # app/views.py

def story_reviews(request, story_id):
    # 1. Fetch story info from Flask to get the Title
    try:
        response = requests.get(f"http://127.0.0.1:5000/stories")
        stories = response.json()
        story = next((s for s in stories if s['id'] == story_id), None)
    except:
        story = {'title': 'Race Track'}

    # 2. Get all reviews from the Django DB
    reviews = StoryRating.objects.filter(story_id=story_id).select_related('user').order_by('-created_at')
    
    return render(request, 'game/story_reviews.html', {
        'story': story,
        'reviews': reviews
    })