
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

with open("secrets/postgres_pass.txt","r") as f:
            postgres_pass = f.read()
engine = create_engine(f"postgresql+psycopg://postgres:{postgres_pass}@localhost/fastapi")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
