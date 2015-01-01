import rabbitmqhandler
import dbhandler
import crawler
import confighandler


def main():
    try:
        config = confighandler.config

        if confighandler.check_config_keys():
            dbh = dbhandler.DBHandler(config)
            rmq = rabbitmqhandler.RabbitMQHandler(config, dbh)
            rmq.daemon = True
            rmq.start()
            my_crawler = crawler.Crawler(config, dbh)
            while(True):
                db_seed = dbh.get_next_unfollowed_user_from_db()
                print '____'*20
                if db_seed:
                    next_to_crawl_list = {'users': db_seed, 'db_seed': True}
                else:
                    next_to_crawl_list = {'users': my_crawler.get_crawling_seed(),
                                          'db_seed': False}
                my_crawler.start_crawling(next_to_crawl_list)
                rmq.pull_users_to_mq()
                print '____'*20
    except KeyboardInterrupt:
        print 'Thanks for playing!'

if __name__ == '__main__':
    main()