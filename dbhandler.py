import time
import logging
import psycopg2

from twitteruser import TwitterUser

logger = logging.getLogger('logger')


class DBHandler():
    def __init__(self, config):
        self.config = config
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
        try:
            for table in self.tables:
                self.cur.execute(
                    'SELECT * FROM pg_rules '
                    'WHERE rulename = \'on_duplicate_ignore\'')
                if not self.cur.fetchone():
                    self.cur.execute(
                        'CREATE RULE "on_duplicate_ignore" AS ON INSERT TO "{'
                        'table}" '
                        'WHERE EXISTS(SELECT 1 FROM {table} WHERE id=NEW.id) '
                        'DO INSTEAD NOTHING;'.format(table=table))
        except Exception as e:
            self.conn.rollback()
            raise
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.cur.close()
        self.conn.close()

    def add_users_to_table_users(self, user_list):
        with DBHandler(self.config) as db:
            for user in user_list:
                query = 'INSERT INTO {table} (id, screen_name, ' \
                        'description, followers_count, friend, lang, ' \
                        'location, name, proc_status, been_followed, ' \
                        'deep_checked) \
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)' \
                    .format(table=self.config['dbtable'])
                data = (user.id, user.screen_name, user.description,
                        user.followers_count, user.friends_count, user.lang,
                        user.location, user.name, 'raw', 'not_followed', False)
                db.execute(query, data)

    def update_user_status(self, user_id, new_status):
        time.sleep(0.1)
        logger.debug('in dbhandler.update_user_status')
        with DBHandler(self.config) as db:
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
        with DBHandler(self.config) as db:
            query = 'UPDATE {table} SET been_followed = %s ' \
                    'WHERE screen_name = %s' \
                .format(table=self.config['dbtable'])
            data = (been_followed, screen_name)
            db.execute(query, data)

    def get_user_from_db_row(self, user_id):
        with DBHandler(self.config) as db:
            query = 'SELECT * FROM {table} WHERE id = {id} ' \
                .format(table=self.config['dbtable'], id=user_id)
            db.execute(query)
            user = TwitterUser()
            user.id, user.screen_name, user.description, \
            user.followers_count, \
            user.friends_count, user.lang, user.location, user.name, \
            user.proc_status, user.been_followed, \
            user.deep_checked = db.fetchone()
        return user