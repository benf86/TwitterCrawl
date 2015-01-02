import twitterhandler


class CrawlingHandler():
    def __init__(self, config, dbhandler):
        self.tw_handler = twitterhandler.TwitterHandler(config)
        self.db_handler = dbhandler
        self.config = config

    def get_crawling_seed(self):
        print 'Trying to get seed user(s) from seed.txt...'
        with open('seed.txt', 'r+') as seed:
            seeders = [screen_name.strip() for screen_name in seed.readlines()
                       if screen_name.strip()]
            return seeders

    def get_next_unfollowed_user_from_db(self):
        print 'Trying to get seed user from database...'
        with self.db_handler as db:
            query = 'SELECT id FROM {table} ' \
                    'WHERE been_followed = \'not_followed\' ' \
                    'AND proc_status = \'accepted\' ' \
                    'ORDER BY followers_count DESC' \
                .format(table=self.config['dbtable'])
            db.execute(query)
            user = db.fetchone()
            if user:
                next_to_crawl = \
                    [self.db_handler.get_user_from_db_row(user[0]).screen_name]
                query = 'UPDATE {table} SET been_followed = \'followed\' ' \
                        'WHERE id = {id}' \
                    .format(table=self.config['dbtable'], id=user[0])
                db.execute(query)
            else:
                next_to_crawl = []
            return next_to_crawl

    def start_crawling(self, screen_name_list_and_source):
        for user in screen_name_list_and_source['users']:
            try:
                if screen_name_list_and_source['db_seed']:
                    self.db_handler.user_followed(user, 'processing')
                self.crawl(user)
                if screen_name_list_and_source['db_seed']:
                    self.db_handler.user_followed(user, 'followed')
            except KeyboardInterrupt as e:
                print 'Something went wrong while crawling. Reverting last ' \
                      'seed\'s been followed to not_followed\nException: {}' \
                    .format(e)
                with self.db_handler as db:
                    self.db_handler.user_followed(user, 'not_followed')

    def crawl(self, user):
        print '\nCrawling user: {}\n'.format(user)
        followers_ids = self.tw_handler.get_followers_ids(user)
        users_from_ids = self.tw_handler.get_users_from_ids(
            followers_ids)
        user_objects = self.tw_handler.parse_users(users_from_ids)
        print '\nAdding users to database (can take a while)...\n'
        self.db_handler.add_users_to_table_users(user_objects)