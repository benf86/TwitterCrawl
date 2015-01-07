import sys
import logging

import twitterhandler
import confighandler
import dbhandler

from crawlerhud import CrawlerHUD

logger = logging.getLogger('logger')


class CrawlingHandler():
    def __init__(self):
        self.tw_handler = twitterhandler.TwitterHandler()
        self.config = confighandler.config

    def get_crawling_seed(self):
        with open('seed.txt', 'r+') as seed:
            seeders = [screen_name.strip() for screen_name in seed.readlines()
                       if screen_name.strip()
                       and ' ignored' not in screen_name]
            if seeders:
                seed.seek(0)
                seed.truncate()
                seed.seek(0)
                seed.writelines(['{} ignored\n'.format(line)
                                 for line in seeders])
        return seeders

    def get_next_unfollowed_user_from_db(self):
        db_handler = dbhandler.DBHandler()
        with db_handler as db:
            query = 'SELECT id FROM {table} ' \
                    'WHERE been_followed = \'not_followed\' ' \
                    'AND proc_status = \'accepted\' ' \
                    'ORDER BY followers_count DESC' \
                .format(table=self.config['dbtable'])
            db.execute(query)
            user = db.fetchone()
            if user:
                next_to_crawl = \
                    [dbhandler.DBHandler().get_user_from_db_row(
                        user[0]).screen_name]
                query = 'UPDATE {table} SET been_followed = \'followed\' ' \
                        'WHERE id = {id}' \
                    .format(table=self.config['dbtable'], id=user[0])
                db.execute(query)
            else:
                next_to_crawl = []
            return next_to_crawl

    def get_10_rejected_users_by_followers_count(self):
        db_handler = dbhandler.DBHandler()
        with db_handler as db:
            query = 'SELECT id FROM {table} ' \
                    'WHERE proc_status = \'rejected\' ' \
                    'AND deep_checked = \'false\' ' \
                    'AND tweets = \'\' ' \
                    'ORDER BY followers_count DESC ' \
                    'LIMIT 10' \
                .format(table=self.config['dbtable'])
            db.execute(query)
            user_tuple = db.fetchall()
            if user_tuple:
                user_list = [user[0] for user in user_tuple]
                return user_list
        return None

    def collect_and_add_statuses(self):
        db_handler = dbhandler.DBHandler()
        ten_best_rejects = self.get_10_rejected_users_by_followers_count()
        statuses = self.tw_handler.get_statuses_from_ids(ten_best_rejects)
        if statuses:
            for user, statuses in statuses.iteritems():
                db_handler \
                    .add_statuses_to_user(user, statuses)

    def start_crawling(self, screen_name_list_and_source):
        db_handler = dbhandler.DBHandler()
        for user in screen_name_list_and_source['users']:
            try:
                if screen_name_list_and_source['db_seed']:
                    db_handler.user_followed(user, 'processing')
                self.crawl(user)
                if screen_name_list_and_source['db_seed']:
                    db_handler.user_followed(user, 'followed')
            except KeyboardInterrupt as e:
                print 'Crawling interrupted. Reverting last seed\'s ' \
                      'been_followed to not_followed and exiting...' \
                    .format(e)
                db_handler.user_followed(user, 'not_followed')
                sys.exit(0)

    def crawl(self, user):
        db_handler = dbhandler.DBHandler()
        try:
            followers_ids = self.tw_handler.get_followers_ids(user)
            if followers_ids and followers_ids[0] \
                    and not followers_ids[0].get('message'):
                users_from_ids = self.tw_handler.get_users_from_ids(
                    followers_ids)
                if users_from_ids:
                    user_objects = self.tw_handler.parse_users(users_from_ids)
                    CrawlerHUD.hud(
                        'Adding users to database (can take a while)...')
                    if user_objects:
                        db_handler.add_users_to_table_users(user_objects)
        except Exception:
            logger.exception('\n')
