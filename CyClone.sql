DROP DATABASE IF EXISTS cyclone;
CREATE DATABASE cyclone;
\c cyclone;


CREATE TABLE Cyclone(
    name VARCHAR(32) PRIMARY KEY,
    formationDate DATE,
    dissipationDate DATE
);


CREATE TABLE Observation(
    idObservation SERIAL PRIMARY KEY,
    cycloneName VARCHAR(32) NOT NULL,
    latitude NUMERIC(12,10) NOT NULL,
	longitude NUMERIC(13,10) NOT NULL,
    observationDate TIMESTAMP NOT NULL,
    observationRadius INT NOT NULL,
    intensity INT CHECK(intensity BETWEEN 1 AND 5),
	CONSTRAINT check_latitude CHECK (latitude BETWEEN -90 AND 90),
	CONSTRAINT check_longitude CHECK (longitude BETWEEN -180 AND 180),
    FOREIGN KEY (cycloneName) REFERENCES Cyclone(name)
);


INSERT INTO Cyclone(name, formationDate, dissipationDate) VALUES
    ('Irma', '2017-08-30', '2017-09-12'),
    ('Katrina', '2005-08-23', '2005-08-31'),
    ('Andrew', '1992-08-16', '1992-08-28');


INSERT INTO Observation(cycloneName, latitude, longitude, observationDate, observationRadius, intensity) VALUES
    ('Irma', 25.789, -80.226, '2017-09-05 12:00:00', 500, '4'),
    ('Irma', 26.123, -79.654, '2017-09-05 18:00:00', 450, '4'),
    ('Irma', 27.000, -79.000, '2017-09-06 00:00:00', 400, '3'),
    ('Katrina', 29.889, -89.684, '2005-08-28 18:00:00', 550, '5'),
    ('Katrina', 30.123, -89.226, '2005-08-29 00:00:00', 600, '5'),
    ('Andrew', 25.500, -80.000, '1992-08-24 18:00:00', 350, '4'),
    ('Andrew', 25.500, -80.000, '1992-08-24 18:00:00', 350, '4');
