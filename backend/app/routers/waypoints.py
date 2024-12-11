# app/routers/waypoints.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.services.waypoint_service import create_waypoint, get_all_waypoints
from pydantic import BaseModel
from typing import List

router = APIRouter()

class WaypointCreate(BaseModel):
    name: str
    latitude: float
    longitude: float
    description: str = None

class WaypointResponse(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    description: str = None

@router.post("/waypoints", response_model=WaypointResponse)
def add_waypoint(waypoint: WaypointCreate, db: Session = Depends(get_db)):
    return create_waypoint(db, **waypoint.dict())

@router.get("/waypoints", response_model=List[WaypointResponse])
def list_waypoints(db: Session = Depends(get_db)):
    return get_all_waypoints(db)
