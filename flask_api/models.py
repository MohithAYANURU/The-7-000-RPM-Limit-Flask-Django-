from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()

class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_page_id = db.Column(db.Integer)

class Page(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    story_id=db.Column(db.Integer, db.ForeignKey('story.id'))
    text=db.Column(db.Text, nullable=False)
    is_ending = db.Column(db.Boolean, default=False)

class Choice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'))
    text = db.Column(db.String(200))
    next_page_id = db.Column(db.Integer)

