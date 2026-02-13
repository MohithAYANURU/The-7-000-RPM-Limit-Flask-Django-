from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()

class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='draft')
    start_page_id = db.Column(db.Integer)

    # CASCADE: When a Story is deleted, all its Pages are deleted
    pages = db.relationship('Page', backref='story', cascade="all, delete-orphan", lazy=True)

class Page(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    story_id=db.Column(db.Integer, db.ForeignKey('story.id'))
    text=db.Column(db.Text, nullable=False)
    is_ending = db.Column(db.Boolean, default=False)
    ending_label = db.Column(db.String(100), nullable=True)

    choices=db.relationship('Choice', backref='story', cascade="all, delete-orphan", lazy=True)


class Choice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'))
    text = db.Column(db.String(200))
    next_page_id = db.Column(db.Integer)

