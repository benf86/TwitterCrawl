import time
import sys
import logging
import logging.config

import dbhandler
import crawlinghandler
import confighandler
import rabbitmqhandler

logging.config.fileConfig('logger.conf')
logger = logging.getLogger('logger')


class Crawler():
    def __init__(self):
        self.config = confighandler.config
        self.dbh = dbhandler.DBHandler(self.config)
        self.rmq = rabbitmqhandler.RabbitMQHandler(self.config, self.dbh)
        self.ch = crawlinghandler.CrawlingHandler(self.config, self.dbh)

    def start_crawling(self):
        my_crawler = crawlinghandler.CrawlingHandler(self.config, self.dbh)
        print 'Crawling is starting. Grab a hot beverage and enjoy!'
        while True:
            self.rmq.pull_users_to_mq()
            db_seed_user = crawlinghandler.CrawlingHandler \
                .get_next_unfollowed_user_from_db(self.ch)
            next_to_crawl_list = \
                {'users': db_seed_user,
                 'db_seed': True} if db_seed_user else \
                    {'users': my_crawler.get_crawling_seed(),
                     'db_seed': False}
            if not next_to_crawl_list:
                print 'No crawling seed available. Sleeping for 10 seconds ' \
                      'and retrying...'
                time.sleep(10)
                continue
            my_crawler.start_crawling(next_to_crawl_list)


if __name__ == '__main__':
    try:
        Crawler().start_crawling()
    except KeyboardInterrupt:
        print 'Thanks for playing!'
        sys.exit(0)
    except Exception as e:
        print 'Critical error. Shutting down...'
        logger.exception('\n')
        sys.exit(0)
