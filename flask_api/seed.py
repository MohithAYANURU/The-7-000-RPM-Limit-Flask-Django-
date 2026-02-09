from app import app, db
from models import Story, Page, Choice

def seed_story():
    with app.app_context():
        # 1. Clear the track
        db.drop_all()
        db.create_all()

        # 2. The Main Story Header
        ford_story = Story(
            title="Le Mans '66: The 7,000 RPM Limit",
            description="The true story of Carroll Shelby, Ken Miles, and the battle to beat Ferrari.",
            status="published" 
        )
        db.session.add(ford_story)
        db.session.commit()

        # 3. Create the Scenes (Pages)
        p1 = Page(story_id=ford_story.id, text="Willow Springs, 1965. The GT40 is a mess. Ken Miles says the brakes are failing at 200mph. Corporate says 'Don't touch it, just drive.' What's your move?")
        
        p2 = Page(story_id=ford_story.id, text="You listen to Ken. You redesign the brakes and the aero. The car is now a beast. You arrive at Le Mans '66. The Ferrari 330 P3 is ahead. Ken wants to push the engine to 7,000 RPM to pass. Do you allow it?")
        
        p3 = Page(story_id=ford_story.id, 
                  text="You ignored Ken to save money. At the first corner of Le Mans, your brakes explode. You crash out in front of Henry Ford II. You're fired. GAME OVER.", 
                  is_ending=True, 
                  ending_label="Corporate Failure")
        
        p4 = Page(story_id=ford_story.id, text="The engine screams but it holds! Ken passes the Ferrari and takes the lead. But now, Ford Executive Leo Beebe orders you to slow down so all three Fords can cross the finish line together for a photo. Ken is furious. What do you tell him?")
        
        p5 = Page(story_id=ford_story.id, 
                  text="Ken slows down. The Fords cross together. But because McLaren started further back on the grid, he is declared the winner on a technicality. Ken is robbed of his win, but his legacy is secure. ENDING.", 
                  is_ending=True, 
                  ending_label="Technicality Defeat")
        
        p6 = Page(story_id=ford_story.id, 
                  text="Ken ignores the order and floors it! He wins Le Mans clearly. Ford is furious you disobeyed corporate, but the world knows who the fastest man is. VICTORY. ENDING.", 
                  is_ending=True, 
                  ending_label="Legendary Victory")

        db.session.add_all([p1, p2, p3, p4, p5, p6])
        db.session.commit()

        # 4. Connect the start
        ford_story.start_page_id = p1.id
        db.session.commit()

        # 5. Create the Choices
        db.session.add(Choice(page_id=p1.id, text="Trust Ken: Redesign the car", next_page_id=p2.id))
        db.session.add(Choice(page_id=p1.id, text="Trust Corporate: Save the money", next_page_id=p3.id))
        db.session.add(Choice(page_id=p2.id, text="Push to 7,000 RPM!", next_page_id=p4.id))
        db.session.add(Choice(page_id=p2.id, text="Play it safe: Stay at 6,000 RPM", next_page_id=p3.id)) 
        db.session.add(Choice(page_id=p4.id, text="Order Ken to slow down for the photo", next_page_id=p5.id))
        db.session.add(Choice(page_id=p4.id, text="Tell Ken to go for the win!", next_page_id=p6.id))

        db.session.commit()
        print("🏁 Ford scenario loaded into Postgres!")

if __name__ == "__main__":
    seed_story()