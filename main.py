import os
import random

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# ---------- DATABASE SETUP ----------

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


class PlayerDB(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    money = Column(Integer, default=100)
    energy = Column(Integer, default=100)
    strength = Column(Integer, default=1)
    agility = Column(Integer, default=1)
    intelligence = Column(Integer, default=1)
    wins = Column(Integer, default=0)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- FASTAPI ----------

app = FastAPI(title="City of Syndicates API")


class Player(BaseModel):
    username: str
    password: str


class Action(BaseModel):
    username: str


@app.get("/")
def root():
    return {"message": "Persistent City of Syndicates backend is running"}


# ---------- AUTH ----------

@app.post("/register")
def register(player: Player, db: Session = Depends(get_db)):
    existing = db.query(PlayerDB).filter(PlayerDB.username == player.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_player = PlayerDB(username=player.username, password=player.password)
    db.add(new_player)
    db.commit()
    db.refresh(new_player)

    return {"message": "Player registered permanently"}


@app.post("/login")
def login(player: Player, db: Session = Depends(get_db)):
    user = db.query(PlayerDB).filter(PlayerDB.username == player.username).first()

    if not user or user.password != player.password:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    return {"message": "Login successful", "money": user.money, "energy": user.energy}


@app.get("/stats/{username}")
def stats(username: str, db: Session = Depends(get_db)):
    user = db.query(PlayerDB).filter(PlayerDB.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "money": user.money,
        "energy": user.energy,
        "wins": user.wins,
        "strength": user.strength,
        "agility": user.agility,
        "intelligence": user.intelligence,
    }


# ---------- CRIME SYSTEM ----------

CRIMES = [
    {"name": "Pickpocket", "energy": 10, "reward": (20, 50), "success": 0.9},
    {"name": "Store Robbery", "energy": 20, "reward": (50, 120), "success": 0.7},
    {"name": "Armored Van Heist", "energy": 40, "reward": (150, 300), "success": 0.5},
]


@app.post("/crime")
def commit_crime(action: Action, db: Session = Depends(get_db)):
    user = db.query(PlayerDB).filter(PlayerDB.username == action.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    crime = random.choice(CRIMES)

    if user.energy < crime["energy"]:
        raise HTTPException(status_code=400, detail="Not enough energy")

    user.energy -= crime["energy"]

    if random.random() <= crime["success"]:
        reward = random.randint(*crime["reward"])
        user.money += reward
        user.wins += 1
        result = {"result": "success", "crime": crime["name"], "money_gained": reward}
    else:
        result = {"result": "failed", "crime": crime["name"]}

    db.commit()
    return result


# ---------- REST ----------

@app.post("/rest")
def rest(action: Action, db: Session = Depends(get_db)):
    user = db.query(PlayerDB).filter(PlayerDB.username == action.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.energy = min(100, user.energy + 20)
    db.commit()

    return {"message": "Energy restored", "energy": user.energy}


# ---------- LEADERBOARD ----------

@app.get("/leaderboard")
def leaderboard(db: Session = Depends(get_db)):
    users = db.query(PlayerDB).order_by(PlayerDB.money.desc()).limit(10).all()
