#!/usr/bin/env python
__author__ = 'amaxilatis'

# required for logging
# required for rabbitmq connections
import pika
# required for mochad communication
from properties import *

import socket

import logging
import logger

logger.log_config()


def netcat(hostname, port, content):
    try:
        print content
        logging.info(" [n] Trying connection to: %s:%s" % (hostname, port))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((hostname, port))

        logging.info(" [n] Connected to: %s:%s" % (hostname, port))
        s.sendall(b"%s\n" % content)
        logging.info(" [n] sent: %s" % content)
        s.shutdown(socket.SHUT_WR)
        buff = ""

        while True:
            data = s.recv(1024)
            if data == "":
                break
            buff = "%s%s" % (buff, data)
        logging.info(" [n] Received: %s" % repr(buff))
        s.close()
        logging.info(" [n] Connection closed.")
        return repr(buff)
    except Exception as ex:
        logging.error(" [n] ERROR: %s" % ex)
        raise ex


# create the rabbitmq exchange and queue names to communicate with sensorflare
send_exchange = "mochad-" + username + "-send"
commands_exchange = "mochad-" + username + "-commands"
commands_queue = "mochad-" + username + "-commands"

logging.info(" [x] send_queue: " + send_exchange)
logging.info(" [x] commands_queue: " + commands_queue)
logging.info(" [x] commands_exchange: " + commands_exchange)

# sensorflare rabbitmq server
sensorflareHost = 'mochad.sensorflare.com'
# create the credentials to communicate with rabbitmq
sensorflareCredentials = pika.credentials.PlainCredentials(username, password)

# function that connects to rabbitmq and listens for commands
def create_connection(host, credentials):
    # create a blocking connection with pika
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, credentials=credentials))
    # open a channel for rabbitmq
    channel = connection.channel()
    logging.info(" [x] connected to 'mochad.sensorflare.com'")
    # declare the commands exchange if missing
    channel.exchange_declare(exchange=commands_exchange, type='topic', durable=True, internal=False, auto_delete=False,passive=True)
    # bind our queue to the exchange
    channel.queue_bind(exchange=commands_exchange, queue=commands_queue)

    def rabbitSend(message):
        try:
            channel.basic_publish(exchange=send_exchange, routing_key=send_exchange, body=message)
        except:
            logging.error(' [x] error sending back message')

    def callback(ch, method, properties, body):
        response = netcat("localhost", 1099, body)
        logging.info(' [c] sent:' + body)
        logging.info(' [c] response:' + response)
        rabbitSend(response[1:-1].replace('\\n', '\n'))

    # set the consume callback
    channel.basic_consume(callback, queue=commands_queue, no_ack=True)

    # start waiting for the commands
    logging.info(' [*] Waiting for commands. To exit press CTRL+C')

    # send a connect message to sensorflare
    rabbitSend('connected\n')

    # start the blocking consume
    try:
        channel.start_consuming()
    except:
        logging.error(' [*] connection was closed!')
        logging.info(' [x] reconnecting in 5 seconds...')
        import time

        time.sleep(5)
        logging.info(' [x] reconnecting...')
        create_connection(host, credentials)

# start the first connection
create_connection(sensorflareHost, sensorflareCredentials)
