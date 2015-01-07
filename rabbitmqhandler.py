import threading
import logging

import pika

import confighandler
import dbhandler

from infoprocessor import InfoProcessor
from workerhud import WorkerHUD

logger = logging.getLogger('logger')


class RabbitMQHandler(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.config = confighandler.config
        self.connection = None
        self.channel = None
        self.host = self.config['rabbithost']
        self.queue = self.config['rabbitqueue']
        self.dbhandler = dbhandler.DBHandler()

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
        rh = RabbitMQHandler()
        with rh as message_queue:
            message_queue.basic_publish(exchange='',
                                        routing_key=rh.queue,
                                        body=body,
                                        properties=pika.BasicProperties(
                                            delivery_mode=2
                                            # make message persistent
                                        ))

    def receive(self):
        rh = RabbitMQHandler()
        WorkerHUD.hud('[*] Waiting for messages')

        def callback(ch, method, properties, body):
            dbh = dbhandler.DBHandler()
            user = dbh.get_user_from_db_row(body)
            if user:
                logger.debug('Starting user processing...')
                InfoProcessor(user, self.dbhandler).run_checks()
                logger.debug('Processing done, sending ACK...')
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.debug('ACK sent...')

        with rh as message_queue:
            message_queue.basic_consume(callback, rh.queue)
            message_queue.start_consuming()

    def pull_users_to_mq(self):
        with self.dbhandler as db:
            query = 'SELECT id from {table} WHERE proc_status = \'raw\' ' \
                    'ORDER BY followers_count DESC' \
                .format(table=self.config['dbtable'])
            db.execute(query)
            logger.debug('\'raw\' users received from DB sorted by followers')
            i = 1
            users = db.fetchall()
            for user_id in users:
                query = 'UPDATE {table} SET proc_status = \'enqueued\' ' \
                        'WHERE id = {id}' \
                    .format(table=self.config['dbtable'],
                            id=user_id[0])
                db.execute(query)
                logger.debug(
                    '\'proc_status\' set to \'enqueued\' for user {}'.format(
                        user_id[0]))
                self.send(str(user_id[0]))
                sent_user = 'Sent user {}/{} to RMQ'.format(i, len(users))
                logger.info(sent_user)
                i += 1