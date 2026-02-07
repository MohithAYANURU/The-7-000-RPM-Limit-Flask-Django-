from app import app, db
from models import Choice, Story, Page

def seed_story():
    with app.app_context():
        db.drop_all()
        db.create_all()


        ferrari_story=Story(
            title="Ferrari: The Prancing Horse",
            description="Take the wheel of the 330 P3 at Maranello. Prove to Enzo that you have the soul of a champion.",
            status="published"  
        )

        db.session.add(ferrari_story)
        db.session.flush()

        p1 = Page(story_id=ferrari_story.id, text="Enzo Ferrari watches from the pit wall. The V12 engine screams behind you. Do you push for a record lap or play it safe to show consistency?")
        p2 = Page(story_id=ferrari_story.id, text="You pushed too hard! The brakes fade entering the Curva Grande. You spin into the gravel. Enzo is not impressed.")
        p3 = Page(story_id=ferrari_story.id, text="Smooth and precise. You clock three identical laps. Enzo nods and points to the Le Mans entry form.") 

        p2.is_ending = True
        p2.ending_label = "Fired from Maranello"
        p3.is_ending = True
        p3.ending_label = "Le Mans Lead Driver"

        db.session.add_all([p1, p2, p3])
        db.session.flush()

        ferrari_story.start_page_id=p1.id

        