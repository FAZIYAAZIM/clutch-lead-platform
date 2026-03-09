import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Use environment variable for database URL, fallback to local SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./clutch.db")

# For SQLite on Render, we need to adjust the path
if DATABASE_URL.startswith("sqlite"):
    # Ensure the database file is in a writable directory
    import tempfile
    db_path = os.path.join(tempfile.gettempdir(), "clutch.db")
    DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()