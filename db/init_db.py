# db/init_db.py
from db.session import engine
from models.base import Base

# Import all models so Base knows about them before creating tables
from models import merchant, transaction

def init_db():
    """Create all tables in the database."""
    print("Initializing database...")
    Base.metadata.create_all(bind=engine)
    print("Done. Tables created successfully.")

if __name__ == "__main__":
    init_db()