import sys
import json
import time
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
            bootstrap_servers='192.168.1.10:9092',
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
    data_cyclone = {
        "id_device": id,
        "latitude": init_coord["init_lat"],
        "longitude": init_coord["init_long"],
        "date": init_coord["date"]
        # Maybe more params here
    }
    print(data_cyclone)
    producer.send(topic_name, data_cyclone)
    time.sleep(1)
    while (True):
        new_coord = gen_coord.new_coordinates(data_cyclone["latitude"], data_cyclone["longitude"])
        data_cyclone = {
        "id_device": id,
        "latitude": new_coord["lat"],
        "longitude": new_coord["long"],
        "date": new_coord["date"]
        # Maybe more params here
        }
        print(data_cyclone)
        producer.send(topic_name, data_cyclone)
        time.sleep(1)


