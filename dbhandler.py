import time
import logging
import psycopg2
import json

from psycopg2.extensions import adapt

import confighandler
from twitteruser import TwitterUser

logger = logging.getLogger('logger')


class DBHandler():
    def __init__(self):
        self.config = confighandler.config
        self.host = self.config['dbhost']
        self.port = self.config['dbport']
        self.user = self.config['dbuser']
        self.password = self.config['dbpass']
        self.db = self.config['db']
        self.tables = [self.config['dbtable']]
        self.conn = None
        self.cur = None


    def __enter__(self):
        self.conn = psycopg2.connect(database=self.db,
                                     user=self.user,
                                     password=self.password,
                                     host=self.host,
                                     port=self.port)
        self.cur = self.conn.cursor()
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.cur.close()
        self.conn.close()

    def add_db_rule_ignore_duplicates(self):
        with DBHandler() as cur:
            try:
                for table in self.tables:
                    cur.execute(
                        'SELECT * FROM pg_rules '
                        'WHERE rulename = \'on_duplicate_ignore\'')
                    if not cur.fetchone():
                        cur.execute(
                            'CREATE RULE "on_duplicate_ignore" AS ON INSERT '
                            'TO "{'
                            'table}" '
                            'WHERE EXISTS(SELECT 1 FROM {table} WHERE '
                            'id=NEW.id) '
                            'DO INSTEAD NOTHING;'.format(table=table))
            except Exception:
                self.conn.rollback()
                raise

    def add_users_to_table_users(self, user_list):
        if user_list:
            with DBHandler() as db:
                query = 'INSERT INTO {table} (id, screen_name, ' \
                        'description, followers_count, friend, lang, ' \
                        'location, name, proc_status, been_followed, ' \
                        'deep_checked, tweets) VALUES ' \
                    .format(table=self.config['dbtable'])
                first_user = True
                values = u''
                for user in user_list:
                    for k, v in user.__dict__.iteritems():
                        if type(v) == unicode:
                            v = v.encode('utf-8')
                            user[k] = v.encode('string_escape')
                        elif type(v) == str:
                            user[k] = v.encode('string_escape')
                    if all([user.id, user.screen_name, user.name]):
                        if not first_user:
                            values += ', '
                        values += ' ({}, \'{}\', \'{}\', {}, {}, \'{}\', ' \
                                  '\'{}\', \'{}\', \'{}\', \'{}\', {}, ' \
                                  '\'{}\')' \
                            .format(user.id, user.screen_name,
                                    user.description, user.followers_count,
                                    user.friends_count, user.lang,
                                    user.location, user.name, 'raw',
                                    'not_followed', False, '')
                        first_user = False
                values = values.replace('\\\'', '\'\'')
                db.execute(query + values)

    def update_user_status(self, user_id, new_status):
        time.sleep(0.01)
        logger.debug('in dbhandler.update_user_status')
        with DBHandler() as db:
            logger.debug('DBHandler prepared in dbhandler.update_user_status')
            query = 'UPDATE {table} SET proc_status = %s WHERE id = %s' \
                .format(table=self.config['dbtable'])
            logger.debug('query prepared in dbhandler.update_user_status')
            data = (new_status, user_id)
            logger.debug('Updating user\'s DB record...')
            db.execute(query, data)
            logger.debug('User\'s DB record updated...')

    def accept_user(self, user_id):
        return self.update_user_status(user_id, 'accepted')

    def reject_user(self, user_id):
        return self.update_user_status(user_id, 'rejected')

    def user_followed(self, screen_name, been_followed):
        with DBHandler() as db:
            query = 'UPDATE {table} SET been_followed = %s ' \
                    'WHERE screen_name = %s' \
                .format(table=self.config['dbtable'])
            data = (been_followed, screen_name)
            db.execute(query, data)

    def get_user_from_db_row(self, user_id):
        with self as db:
            query = 'SELECT * FROM {table} WHERE id = {id} ' \
                .format(table=self.config['dbtable'], id=user_id)
            db.execute(query)
            result = db.fetchone()
            if result:
                user = TwitterUser()
                user.id, user.screen_name, user.description, \
                user.followers_count, \
                user.friends_count, user.lang, user.location, user.name, \
                user.tweets, user.proc_status, user.been_followed, \
                user.deep_checked = result
                return user
        return None

    def add_statuses_to_user(self, user_id, tweets):
        with DBHandler() as db:
            query = 'UPDATE {table} SET tweets = {tweets}, ' \
                    'proc_status = \'raw\' WHERE id = {id}' \
                .format(table=self.config['dbtable'],
                        id=user_id,
                        tweets=adapt(json.dumps(tweets)))
            db.execute(query)