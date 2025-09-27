from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json, os

app = FastAPI()
DATA_FILE = "sessions.json"

@app.post("/save")
async def save_session(request: Request):
    session = await request.json()

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(session)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return {"message": "✅ Session saved"}

@app.get("/sessions")
async def get_sessions():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []
