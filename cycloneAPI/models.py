from sqlalchemy import Column, String, Integer, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Observation(Base):
    __tablename__ = "observation"
    
    idobservation = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cyclonename = Column(String(32), ForeignKey("cyclone.name"))
    latitude = Column(Numeric(12, 10), nullable=False)
    longitude = Column(Numeric(13, 10), nullable=False)
    observationdate = Column(Date, nullable=False)
    observationradius = Column(Integer, nullable=True)
    intensity = Column(Integer, nullable=True)
    
    cyclone = relationship("Cyclone", back_populates="observations")

class Cyclone(Base):
    __tablename__ = "cyclone"
    
    name = Column(String(32), primary_key=True, index=True)
    formationdate = Column(Date, nullable=False)
    dissipationdate = Column(Date)

    observations = relationship("Observation", back_populates="cyclone")

