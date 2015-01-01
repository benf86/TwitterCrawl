import twitterhandler


class Crawler():
    def __init__(self, config, dbhandler):
        self.tw_handler = twitterhandler.TwitterHandler(config)
        self.db_handler = dbhandler
        self.config = config

    def get_crawling_seed(self):
        with open('seed.txt', 'r+') as seed:
            seeders = [screen_name.strip() for screen_name in seed.readlines()
                       if screen_name.strip()]
            return seeders

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