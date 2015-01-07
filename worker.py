import sys
import logging
import logging.config

from threading import Thread

import rabbitmqhandler
import dbhandler
import confighandler

from workerhud import WorkerHUD

logging.config.fileConfig('logger.conf')
logger = logging.getLogger('logger')


class Worker():
    def __init__(self):
        self.config = confighandler.config
        self.dbh = dbhandler.DBHandler()
        self.rmq = rabbitmqhandler.RabbitMQHandler()

    def work(self):
        t1 = Thread(target=WorkerHUD.update_hud_data)
        t1.setDaemon(True)
        t1.start()
        self.rmq.receive()


if __name__ == '__main__':
    try:
        Worker().work()
    except KeyboardInterrupt:
        print 'Thanks for playing!'
        sys.exit(0)
    except Exception as e:
        print 'Critical error. Shutting down...'
        logger.exception('\n')
        sys.exit(0)
