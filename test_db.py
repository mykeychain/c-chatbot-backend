from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

URL = "postgresql+psycopg2://michaelchang@localhost/chatbot1"
engine = create_engine(URL, echo=True)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1;"))
        print("Connected, got:", result.scalar())
except OperationalError as e:
    print("Connection failed:", e)
