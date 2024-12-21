from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from database import SessionLocal, engine
from typing import List
from datetime import date
import models, schemas

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

@app.get("/cyclones/", response_model=List[schemas.Cyclone])
def get_cyclones(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    cyclones = db.query(models.Cyclone).offset(skip).limit(limit).all()
    return cyclones


@app.post("/cyclones/", response_model=schemas.Cyclone)
def create_cyclone(cyclone: schemas.CycloneCreate, db: Session = Depends(get_db)):
    db_cyclone = models.Cyclone(**cyclone.dict())
    db.add(db_cyclone)
    db.commit()
    db.refresh(db_cyclone)
    return db_cyclone


@app.get("/cyclones/{cyclone_name}", response_model=schemas.Cyclone)
def get_cyclone(cyclone_name: str, db: Session = Depends(get_db)):
    cyclone = db.query(models.Cyclone).filter(models.Cyclone.name == cyclone_name).first()
    if cyclone is None:
        raise HTTPException(status_code=404, detail="Cyclone not found")
    return cyclone


@app.post("/observations/", response_model=schemas.Observation)
def create_observation(observation: schemas.ObservationCreate, db: Session = Depends(get_db)):

    # Check if the cyclone exists and create it if not
    cyclone = db.query(models.Cyclone).filter(models.Cyclone.name == observation.cyclone_name).first()
    if not cyclone:
        new_cyclone = models.Cyclone(
            name=observation.cyclone_name,
            formation_date=observation.observation_date.date(),
            dissipation_date=None
        )
        db.add(new_cyclone)
        db.commit()
        db.refresh(new_cyclone)

    db_observation = models.Observation(**observation.dict())
    db.add(db_observation)
    db.commit()
    db.refresh(db_observation)
    return db_observation
    

@app.put("/cyclones/{cyclone_name}/dissipation_date", response_model=schemas.Cyclone)
def update_dissipation_date(cyclone_name: str, dissipation_date: schemas.CycloneUpdate, db: Session = Depends(get_db)):
    # Fetch the cyclone by name
    cyclone = db.query(models.Cyclone).filter(models.Cyclone.name == cyclone_name).first()

    # If the cyclone doesn't exist, raise a 404 error
    if not cyclone:
        raise HTTPException(status_code=404, detail="Cyclone not found")

    # Update the dissipation_date field
    cyclone.dissipation_date = dissipation_date.dissipation_date
    db.commit()  # Save changes to the database
    db.refresh(cyclone)  # Refresh the instance

    return cyclone


@app.get("/cyclones/{observation_date}", response_model=List[schemas.Cyclone])
def get_cyclones_by_observation_date(
    observation_date: date,
    db: Session = Depends(get_db),
):
    # Query observations where the date part matches the provided date
    observations = (
        db.query(models.Observation)
        .filter(func.date(models.Observation.observation_date) == observation_date)
        .all()
    )

    # Extract cyclone names from the observations
    cyclone_names = {obs.cyclone_name for obs in observations}

    # Query cyclones matching the extracted names
    cyclones = db.query(models.Cyclone).filter(models.Cyclone.name.in_(cyclone_names)).all()

    return cyclones