# app/services/waypoint_service.py
from sqlalchemy.orm import Session
from app.models.waypoint_model import Waypoint

def create_waypoint(db: Session, name: str, latitude: float, longitude: float, description: str = None):
    waypoint = Waypoint(name=name, latitude=latitude, longitude=longitude, description=description)
    db.add(waypoint)
    db.commit()
    db.refresh(waypoint)
    return waypoint

def get_all_waypoints(db: Session):
    return db.query(Waypoint).all()
