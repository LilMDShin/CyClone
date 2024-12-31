from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from database import SessionLocal, engine
from typing import List
from datetime import date
import models, schemas

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.get("/cyclones/{cyclonename}", response_model=schemas.Cyclone)
def get_cyclone(cyclonename: str, db: Session = Depends(get_db)):
    cyclone = db.query(models.Cyclone).filter(models.Cyclone.name == cyclonename).first()
    if cyclone is None:
        raise HTTPException(status_code=404, detail="Cyclone not found")
    return cyclone


@app.post("/observations/", response_model=schemas.Observation)
def create_observation(observation: schemas.ObservationCreate, db: Session = Depends(get_db)):

    # Check if the cyclone exists and create it if not
    cyclone = db.query(models.Cyclone).filter(models.Cyclone.name == observation.cyclonename).first()
    if not cyclone:
        new_cyclone = models.Cyclone(
            name=observation.cyclonename,
            formationdate=observation.observationdate.date(),
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
    

@app.put("/cyclones/{cyclonename}/dissipationdate", response_model=schemas.Cyclone)
def update_dissipation_date(cyclonename: str, dissipationdate: schemas.CycloneUpdate, db: Session = Depends(get_db)):
    # Fetch the cyclone by name
    cyclone = db.query(models.Cyclone).filter(models.Cyclone.name == cyclonename).first()

    # If the cyclone doesn't exist, raise a 404 error
    if not cyclone:
        raise HTTPException(status_code=404, detail="Cyclone not found")

    # Update the dissipation_date field
    cyclone.dissipationdate = dissipationdate.dissipationdate
    db.commit()  # Save changes to the database
    db.refresh(cyclone)  # Refresh the instance

    return cyclone


@app.put("/cyclones/{current_name}/rename", response_model=schemas.Cyclone)
def rename_cyclone(current_name: str, new_name: str, db: Session = Depends(get_db)):
    """
    Renames a cyclone. Observations are updated automatically by the database.
    """
    # Check if the new name already exists
    existing_cyclone = db.query(models.Cyclone).filter(models.Cyclone.name == new_name).first()
    if existing_cyclone:
        raise HTTPException(status_code=400, detail="A cyclone with this name already exists.")

    # Fetch the cyclone to rename
    cyclone = db.query(models.Cyclone).filter(models.Cyclone.name == current_name).first()
    if not cyclone:
        raise HTTPException(status_code=404, detail="Cyclone not found.")

    # Update the cyclone name
    cyclone.name = new_name
    db.commit()  # Commit the update; the database handles cascading updates

    db.refresh(cyclone)  # Refresh the cyclone instance
    return cyclone