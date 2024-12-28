from sqlalchemy import Column, String, Integer, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Cyclone(Base):
    __tablename__ = "cyclone"
    
    name = Column(String(32), primary_key=True, index=True)
    formation_date = Column(Date, nullable=False)
    dissipation_date = Column(Date)

    observations = relationship("Observation", back_populates="cyclone")

class Observation(Base):
    __tablename__ = "Observation"
    
    id_observation = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cyclone_name = Column(String(32), ForeignKey("Cyclone.name"))
    latitude = Column(Numeric(12, 10), nullable=False)
    longitude = Column(Numeric(13, 10), nullable=False)
    observation_date = Column(Date, nullable=False)
    observation_radius = Column(Integer, nullable=True)
    intensity = Column(Integer, nullable=True)
    
    cyclone = relationship("Cyclone", back_populates="observations")
