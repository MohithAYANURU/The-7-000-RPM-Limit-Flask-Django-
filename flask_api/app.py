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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Host 0.0.0.0 is required so the Django container can see this app
    app.run(host="0.0.0.0", port=5000)