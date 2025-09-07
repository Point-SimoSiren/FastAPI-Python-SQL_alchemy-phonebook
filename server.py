from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# --- Tietokanta ---
DATABASE_URL = "sqlite:///./phonebook.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# --- Malli ---
class Phonebook(Base):
    __tablename__ = "phonebook"

    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String, index=True)
    lastname = Column(String, index=True)
    number = Column(String, index=True)


# --- FastAPI ---
app = FastAPI()

# Luodaan taulut, jos eivät ole olemassa
Base.metadata.create_all(bind=engine)

# --- DB sessionin riippuvuus ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- API reitit ---
@app.post("/phonebook/", response_model=dict)
def create_entry(firstname: str, lastname: str, number: str, db: Session = Depends(get_db)):
    entry = Phonebook(firstname=firstname, lastname=lastname, number=number)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return {"id": entry.id, "firstname": entry.firstname, "lastname": entry.lastname, "number": entry.number}


@app.get("/phonebook/", response_model=list[dict])
def get_entries(db: Session = Depends(get_db)):
    entries = db.query(Phonebook).all()
    return [{"id": e.id, "firstname": e.firstname, "lastname": e.lastname, "number": e.number} for e in entries]


@app.get("/phonebook/{entry_id}", response_model=dict)
def get_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = db.query(Phonebook).filter(Phonebook.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"id": entry.id, "firstname": entry.firstname, "lastname": entry.lastname, "number": entry.number}


@app.delete("/phonebook/{entry_id}", response_model=dict)
def delete_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = db.query(Phonebook).filter(Phonebook.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(entry)
    db.commit()
    return {"message": f"Entry with id {entry_id} deleted"}
