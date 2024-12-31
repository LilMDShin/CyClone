import sys
import json
import time
import random
import gen_coordinates as gen_coord
from kafka import KafkaProducer
from kafka.errors import KafkaError # type: ignore

topic_name = "cyclone"

# Custom JSON serializer for keys
def json_serializer(data):
    if data is None:
        return None
    return json.dumps(data).encode('utf-8')

# Retry logic
while (True):
    try:
        producer = KafkaProducer(
            bootstrap_servers='broker:9092',
            value_serializer=json_serializer,
            key_serializer=json_serializer,
            acks=1
        )
        break
    except KafkaError as e:
        print("Error connecting to Kafka : ", e)
        time.sleep(1)

# If down and then restarted will prob reinitialize coordinates
if __name__ == "__main__":
    # Command line parameter : id of the device
    id = int(sys.argv[1])
    init_coord = gen_coord.init_coordinates()
    intensity = random.randint(1,5)
    observation_radius = random.randint(1,25)
    cyclone_name = "" + str(id) + " " + init_coord["date"]

    data_cyclone = {
        "id_device": id,
        "latitude": init_coord["init_lat"],
        "longitude": init_coord["init_long"],
        "date": init_coord["date"],
        "cyclone_name": cyclone_name,
        "intensity": intensity,
        "observation_radius": observation_radius
        # Maybe more params here
    }
    print(data_cyclone)
    producer.send(topic_name, data_cyclone, key=id)
    time.sleep(1)
    while (True):
        new_coord = gen_coord.new_coordinates(data_cyclone["latitude"], data_cyclone["longitude"])

        if random.random() < 0.1:  # 10% de chance de changer l'intensité
            data_cyclone["intensity"] = max(1, min(5, data_cyclone["intensity"] + random.choice([-1, 1])))  # Garder entre 1 et 5
        if random.random() < 0.1:  # 10% de chance de changer le rayon
            data_cyclone["observation_radius"] = max(1, min(25, data_cyclone["observation_radius"] + random.randint(-5, 5)))  # Garder entre 1 et 25

        data_cyclone = {
        "id_device": id,
        "latitude": new_coord["lat"],
        "longitude": new_coord["long"],
        "date": new_coord["date"],
        "cyclone_name": data_cyclone["cyclone_name"],
        "observation_radius": data_cyclone["observation_radius"],
        "intensity": data_cyclone["intensity"]
        # Maybe more params here
        }
        print(data_cyclone)
        producer.send(topic_name, data_cyclone, key=id)
        time.sleep(1)


