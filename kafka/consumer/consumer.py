import json
import time
from kafka import KafkaConsumer, KafkaAdminClient
from kafka.admin import NewTopic  # type: ignore
from kafka.errors import KafkaError, TopicAlreadyExistsError # type: ignore

import psycopg2
from datetime import datetime

# Configuration de la BDD
DB_CONFIG = {
    'dbname': 'cyclone',
    'user': 'postgres',
    'password': 'cyclonemdp',
    'host': 'db',
    'port': '5432'
}

# Connexion à la base de données
conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()


# Define topic name
topic_name = "cyclone"

# Custom JSON deserializer for keys
def json_deserializer(data):
    if data is None:
        return None
    return json.loads(data.decode('utf-8'))

# Retry logic
while (True):
    try:
        consumer = KafkaConsumer(
            topic_name,
            group_id='default-group',
            bootstrap_servers='broker:29094',
            value_deserializer=json_deserializer,
            key_deserializer=json_deserializer,
            auto_offset_reset='earliest',
            enable_auto_commit=True
        )
        break
    except KafkaError as e:
        print("Error connecting to Kafka : ", e)
        time.sleep(2)

# Create __consumer_offsets internal topic in case it can't be auto-created
try:
    topic_list = []
    topic_list.append(NewTopic(name="__consumer_offsets", num_partitions=1, replication_factor=1))
    admin_client = KafkaAdminClient(bootstrap_servers='broker:29094')
    admin_client.create_topics(new_topics=topic_list, validate_only=False)
except TopicAlreadyExistsError as err:
    print("Request for topic created is failed as __consumer_offsets is already created due to ", err)
except Exception as err:
    print("Request for topic creation is failing due to ", err)

# Consume messages
try:
    print("Listening for messages on topic ", topic_name, "...")
    # for message in consumer:
    #     print("Received message : ", message.value)
    for message in consumer:
        try:
            # Décodage du message reçu
            data = message.value
            print("Message reçu : ", data)


            # Exemple de message attendu (format JSON) :
            # {
            #     "cyclone_name": "CycloneX",
            #     "latitude": 12.345,
            #     "longitude": 67.890,
            #     "observation_date": "2024-12-26T14:00:00",
            #     "observation_radius": 50,
            #     "intensity": 3
            # }

            observation_date = datetime.strptime(data["date"], "%Y-%m-%d %H:%M:%S")

            # Vérifie si le cyclone existe déjà
            cursor.execute(
                "SELECT name FROM cyclone WHERE name = %s", (data["cyclone_name"],)
            )
            cyclone = cursor.fetchone()

            # Si le cyclone n'existe pas, insère-le
            if not cyclone:
                cursor.execute(
                    """
                    INSERT INTO cyclone (name, formationDate, dissipationDate)
                    VALUES (%s, %s, NULL)
                    """,
                    (data["cyclone_name"], observation_date)
                )
                conn.commit()

            # Insère l'observation
            cursor.execute(
                """
                INSERT INTO observation (
                    cycloneName, latitude, longitude, observationDate, observationRadius, intensity
                ) VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    data["cyclone_name"],
                    data["latitude"],
                    data["longitude"],
                    observation_date,
                    data["observation_radius"],
                    data["intensity"]
                )
            )
            conn.commit()

            print("Données insérées dans la base de données.")

        except Exception as e:
            print(f"Erreur lors de l'insertion des données : {e}")
            conn.rollback()
except Exception as e:
    print("An error occurred : ", e)
finally:
    consumer.close()
