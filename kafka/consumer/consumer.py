import json
import time
from kafka import KafkaConsumer, KafkaAdminClient
from kafka.admin import NewTopic  # type: ignore
from kafka.errors import KafkaError, TopicAlreadyExistsError # type: ignore

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
    for message in consumer:
        print("Received message : ", message.value)
except Exception as e:
    print("An error occurred : ", e)
finally:
    consumer.close()
