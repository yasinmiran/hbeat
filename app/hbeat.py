import os
import pika
import ssl


def publish_heartbeat():
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
        host='public_rmq',  # RabbitMQ host
        port=5671,  # AMQPS port
        virtual_host='/',
        ssl_options=pika.SSLOptions(context),
        credentials=credentials
    )

    # Connect to RabbitMQ
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()

    # Send a "Healthy" message to the default exchange
    channel.basic_publish(
        exchange='amq.default',
        routing_key='some_queue',
        body='Healthy',
        properties=pika.BasicProperties(content_type='text/plain')
    )

    # Close the connection
    connection.close()
    print("Heartbeat sent")


if __name__ == '__main__':
    publish_heartbeat()
