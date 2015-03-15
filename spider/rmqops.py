# -*- coding: utf-8 -*-

import threading

import pika

import confighandler

from infoprocessor import InfoProcessor


class RMQOps(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.config = confighandler.config
        self.connection = None
        self.channel = None
        self.host = self.config['rabbithost']
        self.queue = self.config['rabbitqueue']

    def __enter__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.host))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue, durable=True)
        # Don't send more than 1 message to worker until ack
        self.channel.basic_qos(prefetch_count=1)
        return self.channel

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()

    def run(self):
        self.receive()

    def send(self, body):
        rh = RMQOps()
        with rh as message_queue:
            message_queue.basic_publish(exchange='',
                                        routing_key=rh.queue,
                                        body=body,
                                        properties=pika.BasicProperties(
                                            delivery_mode=2
                                            # make message persistent
                                        ))

    def receive(self):
        rh = RMQOps()

        def callback(ch, method, properties, body):
            user = self.dbops.get_single_user_from_db(body)
            if user:
                InfoProcessor(user, self.dbops).run_checks()
            ch.basic_ack(delivery_tag=method.delivery_tag)

        with rh as message_queue:
            message_queue.basic_consume(callback, rh.queue)
            message_queue.start_consuming()