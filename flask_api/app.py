from flask import Flask, jsonify, request
from models import Choice, db, Story, Page

app = Flask(__name__)
# Update 'mohith' and 'password' as per your local Postgres setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:mohith@localhost:5432/flask_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
db.init_app(app)

@app.route('/stories', methods=['GET'])
def get_stories():
    # Level 13: In a real scenario, you'd filter by status='published' here
    stories = Story.query.all()
    return jsonify([{"id": s.id, "title": s.title, "description": s.description} for s in stories])

@app.route('/stories/<int:story_id>/start', methods=['GET'])
def get_start_page(story_id):
    story = Story.query.get_or_404(story_id)
    return jsonify({"start_page_id": story.start_page_id})

@app.route('/pages/<int:page_id>', methods=['GET'])
def get_page(page_id):
    page = Page.query.get_or_404(page_id)
    choices = Choice.query.filter_by(page_id=page_id).all()

    return jsonify({
        "text": page.text,
        "is_ending": page.is_ending,
        # Level 13: Named endings
        "ending_label": getattr(page, 'ending_label', 'Standard Finish'),
        "choices": [{"text": c.text, "next_page_id": c.next_page_id} for c in choices]
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5000, debug=True)