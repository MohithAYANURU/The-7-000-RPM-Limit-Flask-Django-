from flask import Flask, jsonify, request
from models import Choice, db, Story, Page
import os

app = Flask(__name__)

# Configured for Docker: uses 'db' as hostname
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 
    'postgresql://postgres:mohith@db:5432/flask_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

db.init_app(app)

@app.route('/stories', methods=['GET'])
def get_stories():
    """Returns a list of all available racing storylines."""
    stories = Story.query.all()
    return jsonify([{"id": s.id, "title": s.title, "description": s.description} for s in stories])

@app.route('/stories/<int:story_id>/start', methods=['GET'])
def get_start_page(story_id):
    """Returns the starting page ID for a specific race story."""
    story = Story.query.get_or_404(story_id)
    return jsonify({"start_page_id": story.start_page_id})

@app.route('/pages/<int:page_id>', methods=['GET'])
def get_page(page_id):
    """Returns the text and choices for a specific story page."""
    page = Page.query.get_or_404(page_id)
    choices = Choice.query.filter_by(page_id=page_id).all()

    return jsonify({
        "text": page.text,
        "is_ending": page.is_ending,
        "ending_label": getattr(page, 'ending_label', 'Standard Finish'),
        "choices": [{"text": c.text, "next_page_id": c.next_page_id} for c in choices]
    })


#creating pages and story and choices
@app.route('/stories', methods=['POST'])
def create_story():
    data = request.get_json()
    new_story = Story(
        title=data.get('title'),
        description=data.get('description'),
        status=data.get('status', 'published')
    )
    db.session.add(new_story)
    db.session.commit()
    return jsonify({"id": new_story.id, "message": "Story Registered"}), 201


@app.route('/stories/<int:story_id>/pages', methods=['POST'])
def add_page(story_id):
    data = request.get_json()
    new_page = Page(
        story_id=story_id,
        text=data.get('text'),
        is_ending=data.get('is_ending', False),
        ending_label=data.get('ending_label')
    )
    db.session.add(new_page)
    db.session.commit() # This triggers the Postgres Auto-Increment
    
    # Return the ID so the UI can show "Created Page #X"
    return jsonify({"id": new_page.id, "message": "Scenario added"}), 201



# --- ADD THIS TO YOUR FLASK APP.PY ---

@app.route('/stories/<int:story_id>', methods=['PUT'])
def update_story(story_id):
    """Updates the story metadata, specifically the start_page_id."""
    data = request.get_json()
    story = Story.query.get_or_404(story_id)
    
    if 'start_page_id' in data:
        story.start_page_id = data['start_page_id']
    
    db.session.commit()
    return jsonify({"message": "Start page linked successfully"}), 200


@app.route('/pages/<int:page_id>/choices', methods= ['POST'])
def add_choice(page_id):
    data= request.get_json()
    new_choice = Choice(
        page_id=page_id,
        text=data.get('text'),
        next_page_id=data.get('next_page_id')
    )
    db.session.add(new_choice)
    db.session.commit()

    return jsonify({"id":new_choice.id, "message":"Choice added to story"}), 201



@app.route('/stories/<int:story_id>', methods=['DELETE'])
def delete_story(story_id):
    story = Story.query.get_or_404(story_id)
    
    # SQLAlchemy now handles the deletion of all linked Pages 
    # and those Pages will handle the deletion of all linked Choices.
    db.session.delete(story)
    db.session.commit()
    
    return jsonify({"message": "Race track and all its scenarios demolished"}), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Host 0.0.0.0 is required so the Django container can see this app
    app.run(host="0.0.0.0", port=5000)

    #for django ->app.run(host="0.0.0.0", port=5000)