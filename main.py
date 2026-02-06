from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="City of Syndicates API")

players = {}

class Player(BaseModel):
    username: str
    password: str


@app.get("/")
def root():
    return {"message": "City of Syndicates backend is running"}


@app.post("/register")
def register(player: Player):
    if player.username in players:
        return {"error": "Username already exists"}
    players[player.username] = {"password": player.password, "money": 100, "energy": 100}
    return {"message": "Player registered successfully"}


@app.post("/login")
def login(player: Player):
    if player.username not in players:
        return {"error": "User not found"}
    if players[player.username]["password"] != player.password:
        return {"error": "Wrong password"}
    return {"message": "Login successful", "player": players[player.username]}
