import traceback
import sys

import rabbitmqhandler
import dbhandler
import confighandler


class Worker():
    def __init__(self):
        self.config = confighandler.config
        self.dbh = dbhandler.DBHandler(self.config)
        self.rmq = rabbitmqhandler.RabbitMQHandler(self.config, self.dbh)

    def work(self):
        self.rmq.receive()


if __name__ == '__main__':
    try:
        Worker().work()
    except KeyboardInterrupt:
        print 'Thanks for playing!'
        sys.exit(0)
    except Exception as e:
        print 'Critical error. Shutting down...'
        print '___'*20
        print traceback.format_exc()
        print '___'*20
        sys.exit(0)