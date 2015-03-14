# -*- coding: utf-8 -*-
"""
This module takes care of CRUD.
"""
import json
import psycopg2
from psycopg2.extensions import adapt

import confighandler


class DBOps():
    """
    This class includes all the necessary code for anything to do with the DB.
    """

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

    def get_next_unfollowed_user_from_db(self):
        with self as db:
            query = 'SELECT id, screen_name FROM {table} ' \
                    'WHERE been_followed = \'not_followed\' ' \
                    'AND proc_status = \'accepted\' ' \
                    'ORDER BY followers_count DESC ' \
                    'LIMIT 1' \
                .format(table=self.config['dbtable'])
            db.execute(query)
            user = db.fetchone()
            print('DBOps next unfollowed user: {}'.format(user))
            if user:
                next_to_crawl = user[1]
                query = 'UPDATE {table} SET been_followed = \'followed\' ' \
                        'WHERE id = {id}' \
                    .format(table=self.config['dbtable'], id=user[0])
                db.execute(query)
            else:
                next_to_crawl = None
            return next_to_crawl

    def save_users_to_db(self, user_list):
        """
        Save the list of users to database (1 user/row).

        :param user_list: list of user objects - parsed TwApi JSON
        """
        if user_list:
            with self as db:
                query = 'INSERT INTO {table} (id, screen_name, ' \
                        'description, followers_count, friend, lang, ' \
                        'location, name, proc_status, been_followed, ' \
                        'deep_checked, tweets) VALUES ' \
                    .format(table=self.config['dbtable'])
                values = u''
                for user in user_list:
                    if all([user[u'id'], user[u'screen_name'], user[u'name']]):
                        if user_list.index(user) > 0:
                            values += ', '
                        for k in u'screen_name, description, \
                                lang, location, name'.split(', '):
                            k = k.encode('utf-8').strip()
                            user[k] = user[k].encode('utf-8') \
                                .encode('string_escape')
                        values += u' ({}, \'{}\', \'{}\', {}, {}, \'{}\', ' \
                                  u'\'{}\', \'{}\', \'{}\', \'{}\', {}, ' \
                                  u'\'{}\')' \
                            .format(user[u'id'], user[u'screen_name'],
                                    user[u'description'],
                                    user[u'followers_count'],
                                    user[u'friends_count'], user[u'lang'],
                                    user[u'location'], user[u'name'], u'raw',
                                    u'not_followed', False, u'')
                        values = values.encode('utf-8')
                values = values.replace('\\\'', '\'\'')
                db.execute(query + values)

    def update_user_status(self, user_id_or_screen_name, new_status):
        """
        Set a users status (accepted/rejected).

        :param user_id_or_screen_name: string
        :param new_status: 'accepted' or 'rejected'
        """
        try:
            float(user_id_or_screen_name)
            search_by = 'id'
        except ValueError:
            search_by = 'screen_name'
        with self as db:
            query = 'UPDATE {table} SET proc_status = %s \
                WHERE {search_by} = %s' \
                .format(table=self.config['dbtable'], search_by=search_by)
            data = (new_status, user_id_or_screen_name)
            db.execute(query, data)

    def accept_user(self, user_id_or_screen_name):
        """
        Execute update_user_status(user_id_or_screen_name, 'accepted').

        :param user_id_or_screen_name: string
        """
        self.update_user_status(user_id_or_screen_name, 'accepted')

    def reject_user(self, user_id_or_screen_name):
        """
        Execute update_user_status(user_id_or_screen_name, 'rejected').

        :param user_id_or_screen_name: string
        """
        self.update_user_status(user_id_or_screen_name, 'rejected')

    def update_user_followed(self, screen_name, been_followed):
        """
        Set user's been_followed status.

        :param screen_name: string
        :param been_followed: 'processing' or 'followed' or 'not_followed'
        """
        with self as db:
            query = 'UPDATE {table} SET been_followed = %s ' \
                    'WHERE screen_name = %s' \
                .format(table=self.config['dbtable'])
            data = (been_followed, screen_name)
            db.execute(query, data)

    def get_single_user_from_db(self, user_id):
        """
        Get a single user with all his properties from the database.

        :param user_id: string
        :return: user object or None
        """
        with self as db:
            query = 'SELECT * FROM {table} WHERE id = {id} ' \
                .format(table=self.config['dbtable'], id=user_id)
            db.execute(query)
            result = db.fetchone()
            if result:
                user = {}
                user.id, user.screen_name, user.description, \
                user.followers_count, \
                user.friends_count, user.lang, user.location, user.name, \
                user.tweets, user.proc_status, user.been_followed, \
                user.deep_checked = result
                return user
        return None

    def add_statuses_to_user(self, user_id, tweets):
        """
        Add tweets to a users database entry.

        :param user_id: string
        :param tweets: json-dumpsed tweets
        """
        with self as db:
            query = 'UPDATE {table} SET tweets = {tweets}, ' \
                    'proc_status = \'raw\' WHERE id = {id}' \
                .format(table=self.config['dbtable'],
                        id=user_id,
                        tweets=adapt(json.dumps(tweets)))
            db.execute(query)