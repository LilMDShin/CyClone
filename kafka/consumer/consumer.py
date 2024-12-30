import asyncio
import json
from aiokafka import AIOKafkaConsumer
from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from aiokafka.errors import KafkaError, TopicAlreadyExistsError
from websockets import serve
import psycopg2
from datetime import datetime

DB_CONFIG = {
    'dbname': 'cyclone',
    'user': 'postgres',
    'password': 'cyclonemdp',
    'host': 'db',
    'port': '5432'
}

TOPIC_NAME = "cyclone"
KAFKA_BROKER = "broker:29094"

connected_clients = set()

async def create_kafka_consumer():
    while True:
        try:
            consumer = AIOKafkaConsumer(
                TOPIC_NAME,
                bootstrap_servers=KAFKA_BROKER,
                group_id='default-group',
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='earliest',
                enable_auto_commit=True
            )
            await create_topic()
            await consumer.start()
            print("[KAFKA] Consommateur Kafka créé avec succès.")
            return consumer
        except KafkaError as e:
            print(f"[KAFKA] Erreur de connexion à Kafka : {e}. Retentative dans 2 secondes...")
            await asyncio.sleep(2)

async def create_topic():
    admin_client = AIOKafkaAdminClient(bootstrap_servers=KAFKA_BROKER)
    await admin_client.start()
    try:
        topic_list = [NewTopic(name="__consumer_offsets", num_partitions=1, replication_factor=1)]
        await admin_client.create_topics(new_topics=topic_list, validate_only=False)
        print(f"[KAFKA] Topic '__consumer_offsets' créé avec succès.")
    except TopicAlreadyExistsError:
        print(f"[KAFKA] Le topic '{TOPIC_NAME}' existe déjà.")

    try:
        topic_list = [NewTopic(name=TOPIC_NAME, num_partitions=1, replication_factor=1)]
        await admin_client.create_topics(new_topics=topic_list, validate_only=False)
        print(f"[KAFKA] Topic '{TOPIC_NAME}' créé avec succès.")
    except TopicAlreadyExistsError:
        print(f"[KAFKA] Le topic '{TOPIC_NAME}' existe déjà.")
    finally:
        await admin_client.close()

async def ws_handler(websocket):
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"[DEBUG] Message reçu : {message}")
    except Exception as e:
        print(f"[ERROR] Exception dans ws_handler : {e}")
    finally:
        connected_clients.remove(websocket)

async def broadcast_kafka_messages(consumer):
    print("[KAFKA] Début de la consommation des messages Kafka...")
    try:
        async for message in consumer:
            data = message.value
            print(f"[KAFKA] Message reçu de Kafka: {data}")

            # Format date handling
            try:
                # Try first format (2024-12-26T14:00:00)
                observation_date = datetime.strptime(data["observation_date"], "%Y-%m-%dT%H:%M:%S")
            except (KeyError, ValueError):
                try:
                    # Try second format (2024-12-26 14:00:00)
                    observation_date = datetime.strptime(data["date"], "%Y-%m-%d %H:%M:%S")
                except (KeyError, ValueError) as e:
                    print(f"[ERROR] Format de date invalide: {e}")
                    continue

            try:
                # Broadcast to WebSocket clients
                if connected_clients:
                    msg_str = json.dumps(data)
                    await asyncio.gather(*[client.send(msg_str) for client in connected_clients])
                
                # Database operations
                conn = psycopg2.connect(**DB_CONFIG)
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT name FROM cyclone WHERE name = %s", 
                    (data["cyclone_name"],)
                )
                cyclone = cursor.fetchone()

                if not cyclone:
                    cursor.execute(
                        """
                        INSERT INTO cyclone (name, formationDate, dissipationDate)
                        VALUES (%s, %s, NULL)
                        """,
                        (data["cyclone_name"], observation_date)
                    )

                cursor.execute(
                    """
                    INSERT INTO observation (
                        cycloneName, latitude, longitude, observationDate, 
                        observationRadius, intensity
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        data["cyclone_name"],
                        data["latitude"],
                        data["longitude"],
                        observation_date,
                        data.get("observation_radius"),
                        data.get("intensity")
                    )
                )
                
                conn.commit()
                cursor.close()
                conn.close()
                print("[DB] Données insérées dans la base de données.")

            except Exception as e:
                print(f"[DB] Erreur lors de l'insertion des données : {e}")
                if 'conn' in locals():
                    conn.rollback()
                if 'cursor' in locals() and cursor:
                    cursor.close()
                if 'conn' in locals() and conn:
                    conn.close()

    except Exception as e:
        print(f"[KAFKA] Erreur dans broadcast_kafka_messages: {str(e)}")
    finally:
        await consumer.stop()

async def main():
    consumer = await create_kafka_consumer()
    websocket_server = await serve(ws_handler, "0.0.0.0", 8765)
    kafka_task = asyncio.create_task(broadcast_kafka_messages(consumer))
    await asyncio.gather(asyncio.Future(), kafka_task)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"[ERROR] Exception non gérée : {e}")
