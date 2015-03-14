# -*- coding: utf-8 -*-
"""
This module serves as the spider executable.

It takes care of launching threads for all separate processes and kicks them
off initially.
"""

import time

import confighandler
import dbops
import apiops


class Spider():
    """
    Main crawler class.
    """

    def __init__(self):
        """
        Load the configuration.
        """
        self.config = confighandler.config
        self.dbops = dbops.DBOps()
        self.apiops = apiops.APIOps()

    def get_seed_users(self):
        """
        Get the seed user(s) whom to start with
        :return: list of strings - usernames
        """
        usernames = []
        with open('seed.txt') as f:
            for line in f.readlines():
                usernames.append(line.strip())
        return usernames

    def crawl(self):
        """
        Start crawling down the user tree and putting them in the database,
        starting with the manually selected users.
        """
        seed_users = self.get_seed_users()
        self.dbops.save_users_to_db(
            self.apiops.get_user_data(seed_users))
        for user in seed_users:
            self.dbops.accept_user(user)

        for _ in xrange(3):  # replace with while True
            next_user = self.dbops.get_next_unfollowed_user_from_db()
            print('Next user: {}'.format(next_user))
            if not next_user:
                time.sleep(10)
                continue
            followers = self.apiops.get_user_followers_from_api(next_user)
            followers = [follower.encode('utf-8') for follower in followers]
            for followers_chunk in self.chunks(followers, 100):

                self.dbops.save_users_to_db(
                    self.apiops.get_user_data(csv_id_list=followers_chunk))

    def chunks(self, l, n):
        """
        Yield successive n-sized chunks from l.

        :param l: list
        :param n: chunk size
        :yield: chunks
        """
        if l and n:
            for i in xrange(0, len(l), n):
                yield l[i:i + n]
        else:
            pass


if __name__ == '__main__':
    Spider().crawl()