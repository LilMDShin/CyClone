from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

class ObservationBase(BaseModel):
    latitude: float
    longitude: float
    observation_date: datetime
    observation_radius: int
    intensity: Optional[int]

class ObservationCreate(ObservationBase):
    cyclone_name: str

class Observation(ObservationBase):
    id_observation: int
    cyclone_name: str

    class Config:
        from_attributes = True

class CycloneBase(BaseModel):
    name: str
    formation_date: datetime
    dissipation_date: Optional[datetime] = False

class CycloneCreate(CycloneBase):
    pass

class Cyclone(CycloneBase):
    observations: List[Observation] = []

    class Config:
        from_attributes = True

class CycloneUpdate(BaseModel):
    name: Optional[str] = None
    dissipation_date: Optional[date] = None