# test_phonebook.py

''' Testit ei vielä toimi, vika ei ole selvillä '''

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from main import app, get_db  # oletetaan että FastAPI app ja get_db-funktio on main.py:ssa
from main import Base, Phonebook

# 1. Luo testitietokanta (SQLite in-memory)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 2. Luo taulut testitietokantaan
Base.metadata.create_all(bind=engine)

# 3. Korvaa get_db funktio testitietokantaan
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# 4. Testit
def test_create_phonebook_entry():
    response = client.post("/phonebook", json={
        "firstname": "Matti",
        "lastname": "Meikäläinen",
        "number": "0401234567"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["firstname"] == "Matti"
    assert data["lastname"] == "Meikäläinen"
    assert data["number"] == "0401234567"

def test_get_phonebook_entries():
    # Lisää ensin testidata
    db: Session = next(override_get_db())
    entry = Phonebook(firstname="Liisa", lastname="Virtanen", number="0507654321")
    db.add(entry)
    db.commit()

    response = client.get("/phonebook")
    assert response.status_code == 200
    data = response.json()
    assert any(e["lastname"] == "Virtanen" for e in data)
