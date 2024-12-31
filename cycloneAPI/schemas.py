from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

class ObservationBase(BaseModel):
    latitude: float
    longitude: float
    observationdate: datetime
    observationradius: int
    intensity: Optional[int]

class ObservationCreate(ObservationBase):
    cyclonename: str

class Observation(ObservationBase):
    idobservation: int
    cyclonename: str

    class Config:
        from_attributes = True

class CycloneBase(BaseModel):
    name: str
    formationdate: datetime
    dissipationdate: Optional[datetime] = False

class CycloneCreate(CycloneBase):
    pass

class Cyclone(CycloneBase):
    observations: List[Observation] = []

    class Config:
        from_attributes = True

class CycloneUpdate(BaseModel):
    name: Optional[str] = None
    dissipationdate: Optional[datetime] = None