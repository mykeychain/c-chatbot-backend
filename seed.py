import datetime
from database import SessionLocal
from models import User, Bot

def seed_initial_data():
    db = SessionLocal()

    try:
        new_user = User()
        new_user.id = "1"

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
        if not db.query(Bot).first():
            db.add(new_bot)
            db.add(second_bot)
            db.commit
            print(f"✅ Created bot with id={new_bot.id!r}")

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
