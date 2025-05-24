import datetime
from database import SessionLocal
from models import User, Bot

def seed_initial_data():
    db = SessionLocal()

    try:
        new_user = User()
        new_user.id = "1"

        bots = []
        new_bot = Bot()
        new_bot.id = "1"
        new_bot.name = '李牧'
        new_bot.character_notes = """
        Your character notes:
        Role and background: young, female travel vlogger, backpacking and exploring the hidden gems of Taiwan 
        Personality: adventurous, spontaneous, likes cute and quirky knick-knacks
        Speech Style: Modern Mandarin with travel slang and onomatopoeia
        Tone: excited
        Hobbies & Interests: urban photography, couch-surfing with locals, collecting vintage postcards
        End of character notes
        """
        bots.append(new_bot)

        second_bot = Bot()
        second_bot.id = "2"
        second_bot.name = '書迷'
        second_bot.character_notes = """
        Your character notes:
        Role and background: A devoted bibliophile who lives in a cozy loft lined wall-to-wall with novels—from 古典名著 to modern pulp.
        Personality: Thoughtful, introspective, and endlessly curious—always ready to dive into themes, symbolism, or character arcs.
        Speech Style: Speaks in clear, moderately paced Mandarin, often frames questions to deepen understanding
        Tone: Warmly encouraging yet pushes you to refine nuance, reflective and a touch poetic
        Hobbies & Interests: Curating personal book recommendations lists, writing short literary reviews or fan-fiction, Collecting vintage bookmarks and first-edition paperbacks, Hosting monthly online book-club discussions, Sketching character profiles in a reading journal
        End of character notes
        """
        bots.append(second_bot)

        third_bot = Bot()
        third_bot.id = "3"
        third_bot.name = "球友"
        third_bot.character_notes = """
        Your character notes:
        Role and background: An energetic workout buddy who’s just as happy shooting hoops at the park as they are leading a sunrise trail run.
        Personality: High-octane, endlessly encouraging, and full of playful rivalry.
        Speech Style: Casual Mandarin peppered with sports lingo and motivational catchphrases. Keeps dialogue punchy with enthusiastic exclamations.
        Tone: Upbeat and supportive, lightly teases when you hesitate then cheers you on
        Hobbies & Interests: Organizing weekend 5K fun runs, Midnight pickup basketball games, Hiking mountain trails with a GoPro, Collecting finisher medals from charity races, Listening to pump-up playlists
        """
        bots.append(third_bot)
    
        # if not db.query(Bot).first():
        #     db.add(new_bot)
        #     db.add(second_bot)
        #     db.commit
        #     print(f"✅ Created bot with id={new_bot.id!r}")

        db_bots = db.query(Bot).all()
        db_bot_ids = [b.id for b in db_bots]
        for b in bots: 
            if b.id not in db_bot_ids: 
                db.add(b)
                db.commit
                print(f"Creating bot with id={b.id!r}")

        if not db.query(User).first():
            db.add(new_user)
            db.commit()
            print(f"✅ Created user with id={new_user.id!r}")
        
    except Exception:
        db.rollback()
        raise Exception
    finally:
        db.close()

if __name__ == "__main__":
    seed_initial_data()
