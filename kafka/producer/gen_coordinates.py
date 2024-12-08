import random
import datetime

def init_coordinates():
    min_lat = -90
    max_lat = 90
    min_long = -180
    max_long = 180
    lat = random.randint(min_lat, max_lat)
    long = random.randint(min_long, max_long)
    date = datetime.datetime.now(datetime.timezone.utc)
    # Example for the date format : '2024-12-04 16:51:11'
    date = date.strftime("%Y-%m-%d %H:%M:%S")
    init_coord = {
        "init_lat": lat,
        "init_long": long,
        "date": date
    }
    return(init_coord)

def new_coordinates(old_lat, old_long):
    lat_displacement = random.uniform(-0.01, 0.01)
    long_displacement = random.uniform(-0.01, 0.01)
    new_lat = old_lat + lat_displacement
    new_long = old_long + long_displacement
    date = datetime.datetime.now(datetime.timezone.utc)
    date = date.strftime("%Y-%m-%d %H:%M:%S")
    new_coord = {
        "lat": new_lat,
        "long": new_long,
        "date": date
    }
    return(new_coord)