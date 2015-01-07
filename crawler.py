import time
import sys
import logging
import logging.config

from threading import Thread

import dbhandler
import crawlinghandler
import confighandler
import rabbitmqhandler
import twitterhandler

from crawlerhud import CrawlerHUD


logging.config.fileConfig('logger.conf')
logger = logging.getLogger('logger')


class Crawler():
    def __init__(self):
        self.config = confighandler.config
        self.dbh = dbhandler.DBHandler()
        self.th = twitterhandler.TwitterHandler()
        self.rmq = rabbitmqhandler.RabbitMQHandler()
        self.ch = crawlinghandler.CrawlingHandler()
        self.dbh.add_db_rule_ignore_duplicates()

    def users_to_db(self):
        CrawlerHUD.hud('User hunter thread started!')
        while True:
            db_seed_user = crawlinghandler.CrawlingHandler \
                .get_next_unfollowed_user_from_db(self.ch)
            next_to_crawl_list = \
                {'users': db_seed_user,
                 'db_seed': True} if db_seed_user else \
                    {'users': self.ch.get_crawling_seed(),
                     'db_seed': False}
            if not next_to_crawl_list['users']:
                CrawlerHUD.hud(
                    'No crawling seed available. Sleeping for 10 seconds '
                    'and retrying...')
                time.sleep(10)
                continue
            self.ch.start_crawling(next_to_crawl_list)
            time.sleep(2)

    def statuses_to_db(self):
        CrawlerHUD.hud('Tweet hunter thread started!')
        while True:
            self.ch.collect_and_add_statuses()
            time.sleep(2)

    def users_to_mq(self):
        CrawlerHUD.hud('Work balancer thread started!')
        while True:
            self.rmq.pull_users_to_mq()
            time.sleep(2)

    def activate_crawler(self):
        threads = []
        if not threads:
            threads.append(Thread(target=self.users_to_mq))
            threads.append(Thread(target=self.statuses_to_db))
            threads.append(Thread(target=self.users_to_db))
        for thread in threads:
            thread.setDaemon(True)
            thread.start()
        while threads:
            if any(thread.isAlive() == False for thread in threads):
                print 'One of the threads has died. Please restart the ' \
                      'program. Exiting...'
                sys.exit(0)
            time.sleep(60)


if __name__ == '__main__':
    try:
        Crawler().activate_crawler()
    except KeyboardInterrupt:
        print 'Thanks for playing!'
        sys.exit(0)
    except Exception as e:
        print 'Critical error. Shutting down...'
        logger.exception('\n')
        sys.exit(0)
