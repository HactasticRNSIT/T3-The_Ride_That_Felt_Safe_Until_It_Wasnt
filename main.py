from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db
from supabase import create_client
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv

load_dotenv()

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {"databaseURL": os.getenv("FIREBASE_DB_URL")})

supabase_client = None

def get_supabase():
    global supabase_client
    if supabase_client is None:
        supabase_client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    return supabase_client

app = FastAPI(title="SafeMesh API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScoreRequest(BaseModel):
    driver_id: str


class HeartbeatRequest(BaseModel):
    ride_id: str
    role: str
    lat: float
    lng: float


class ReportRequest(BaseModel):
    driver_id: str
    report_text: str
    tags: List[str] = []


@app.get("/health")
async def health():
    try:
        return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/score")
async def score(request: ScoreRequest):
    try:
        client = get_supabase()
        result = client.table("drivers").select("*").eq("driver_id", request.driver_id).execute()
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="Driver not found")
        driver = result.data[0]
        return {
            "driver_id": driver["driver_id"],
            "name": driver["name"],
            "hermesh_score": driver["hermesh_score"],
            "safesignal_score": driver["safesignal_score"],
            "composite_score": driver["safescore"],
            "status": driver["status"],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/heartbeat")
async def heartbeat(request: HeartbeatRequest):
    try:
        if request.role not in ("passenger", "driver"):
            raise HTTPException(status_code=400, detail="role must be passenger or driver")
        timestamp = datetime.utcnow().isoformat()
        db.reference(f"/rides/{request.ride_id}/{request.role}_gps").set({
            "lat": request.lat,
            "lng": request.lng,
            "timestamp": timestamp,
        })
        return {
            "status": "ok",
            "path": f"/rides/{request.ride_id}/{request.role}_gps",
            "timestamp": timestamp,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/risk/{driver_id}")
async def risk(driver_id: str):
    try:
        client = get_supabase()
        result = client.table("micro_reports").select("*").eq("driver_id", driver_id).execute()
        count = len(result.data) if result.data else 0
        risk_flag = count >= 3
        return {"driver_id": driver_id, "total_reports": count, "risk_flag": risk_flag}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/report")
async def report(request: ReportRequest):
    try:
        client = get_supabase()
        client.table("micro_reports").insert({
            "driver_id": request.driver_id,
            "report_text": request.report_text,
            "tags": request.tags,
        }).execute()
        return {"status": "stored", "driver_id": request.driver_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)