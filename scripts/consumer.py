from kafka import KafkaConsumer


def consumers(topic):
    consumer = KafkaConsumer(topic, bootstrap_servers='192.168.100.21:9092')
    for msg in consumer:
        print((msg.value).decode('utf8'))


if __name__ == '__main__':
    # consumers("gender")
    # consumers("cat_result")
    # consumers("province_result")
    # consumers("age_result")
    # consumers("action_result")
    consumers("message_result")