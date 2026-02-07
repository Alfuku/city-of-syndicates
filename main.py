from fastapi import FastAPI
from pydantic import BaseModel
import random

app = FastAPI(title="City of Syndicates API")

players = {}


# ---------- MODELS ----------

class Player(BaseModel):
    username: str
    password: str


class Action(BaseModel):
    username: str


# ---------- BASIC ROUTES ----------

@app.get("/")
def root():
    return {"message": "City of Syndicates backend is running"}


@app.post("/register")
def register(player: Player):
    if player.username in players:
        return {"error": "Username already exists"}

    players[player.username] = {
        "password": player.password,
        "money": 100,
        "energy": 100,
        "strength": 1,
        "agility": 1,
        "intelligence": 1,
        "wins": 0
    }

    return {"message": "Player registered successfully"}


@app.post("/login")
def login(player: Player):
    if player.username not in players:
        return {"error": "User not found"}

    if players[player.username]["password"] != player.password:
        return {"error": "Wrong password"}

    return {"message": "Login successful", "player": players[player.username]}


@app.get("/stats/{username}")
def stats(username: str):
    if username not in players:
        return {"error": "User not found"}
    return players[username]


# ---------- CRIME SYSTEM ----------

CRIMES = [
    {"name": "Pickpocket", "energy": 10, "reward": (20, 50), "success": 0.9},
    {"name": "Store Robbery", "energy": 20, "reward": (50, 120), "success": 0.7},
    {"name": "Armored Van Heist", "energy": 40, "reward": (150, 300), "success": 0.5},
]


@app.post("/crime")
def commit_crime(action: Action):
    if action.username not in players:
        return {"error": "User not found"}

    player = players[action.username]

    crime = random.choice(CRIMES)

    if player["energy"] < crime["energy"]:
        return {"error": "Not enough energy"}

    player["energy"] -= crime["energy"]

    if random.random() <= crime["success"]:
        reward = random.randint(*crime["reward"])
        player["money"] += reward
        player["wins"] += 1
        return {
            "result": "success",
            "crime": crime["name"],
            "money_gained": reward,
            "player": player,
        }
    else:
        return {
            "result": "failed",
            "crime": crime["name"],
            "player": player,
        }


# ---------- ENERGY REGEN (simple manual endpoint) ----------

@app.post("/rest")
def rest(action: Action):
    if action.username not in players:
        return {"error": "User not found"}

    players[action.username]["energy"] = min(
        100, players[action.username]["energy"] + 20
    )

    return {"message": "Energy restored", "player": players[action.username]}


# ---------- LEADERBOARD ----------

@app.get("/leaderboard")
def leaderboard():
    sorted_players = sorted(
        players.items(),
        key=lambda x: x[1]["money"],
        reverse=True
    )

    return [
        {"username": username, "money": data["money"], "wins": data["wins"]}
        for username, data in sorted_players[:10]
    ]
