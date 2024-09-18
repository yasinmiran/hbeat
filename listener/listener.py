import os
import ssl

import pika


def callback(ch, method, properties, body):
    print(f"Received message: {body.decode()}")


def listen_for_heartbeat():
    # Get RabbitMQ connection details from environment variables
    user = os.getenv('RABBITMQ_USER', 'user')
    password = os.getenv('RABBITMQ_PASS', 'password')

    # Define connection parameters with SSL for AMQPS
    context = ssl.create_default_context(
        cafile="/etc/ssl/certs/ca_certificate.pem",
    )
    context.load_cert_chain(
        "/etc/ssl/certs/client_certificate.pem",
        "/etc/ssl/certs/client_key.pem"
    )

    credentials = pika.PlainCredentials(user, password)
    connection_params = pika.ConnectionParameters(
        host='localhost',
        port=5671,
        virtual_host='/',
        ssl_options=pika.SSLOptions(context),
        credentials=credentials
    )

    # Connect to RabbitMQ
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()

    # Declare the queue to ensure it exists
    channel.queue_declare(queue='queue', durable=True)

    # Set up subscription on the queue
    channel.basic_consume(
        queue='queue',  # The queue we are listening to
        on_message_callback=callback,  # Function to call when a message arrives
        auto_ack=True  # Automatically acknowledge receipt of messages
    )

    print("Waiting for heartbeat messages. To exit press CTRL+C")
    channel.start_consuming()


if __name__ == '__main__':
    listen_for_heartbeat()
