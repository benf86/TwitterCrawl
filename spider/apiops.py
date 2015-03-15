# -*- coding: utf-8 -*-
"""
This module takes care of TWs API operations.
"""
import calendar
import time

from TwitterAPI import TwitterAPI
from TwitterAPI import TwitterError

import confighandler



# API request limiting control values - remaining requests
api_limits = {'followers/ids': -1,
              'users/lookup': -1,
              'statuses/user_timeline': -1}
current_time = calendar.timegm(time.gmtime())
api_limits_reset = {'followers/ids': current_time,
                    'users/lookup': current_time,
                    'statuses/user_timeline': current_time}
requests_processed = 0


class APIOps():
    """
    This class includes everything required to make the TW API suffer.
    """

    def __init__(self):
        self.config = confighandler.config
        self.api_key = self.config['twapikey']
        self.api_secret = self.config['twapisecret']
        self.access_token = self.config['twaccess']
        self.access_token_secret = self.config['twaccesssecret']
        self.api = TwitterAPI(self.api_key,
                              self.api_secret,
                              self.access_token,
                              self.access_token_secret)
        self.ignored_users = []
        self.api_limits = api_limits
        self.api_limits_reset = api_limits_reset

    def limited(self, request_type):
        print(self.api_limits[request_type])
        print(self.api_limits_reset[request_type])
        if self.api_limits[request_type] <= 0 and \
                self.api_limits_reset[request_type] > calendar.timegm(
                    time.gmtime()):
            return True
        return False

    def get_user_followers_from_api(self, username):
        """
        Get 5000 followers of the user.

        :param username: string
        :return: list of users' followers
        """
        request = ('followers/ids',
                   {'screen_name': username, 'count': 5000,
                    'stringify_ids': True})
        return self.execute_api_call(request)

    def get_user_data(self, csv_username_list=[], csv_id_list=[]):
        """
        Get user data for up to a 100 users.

        screen_name in request is a csv list of usernames

        :param csv_username_list: list of usernames to look up
        :return: list of user objects
        """
        looking_by = 'user_id' if len(csv_id_list) > 0 else 'screen_name'
        lookup_list = csv_username_list or csv_id_list
        lookup_list = ', '.join(lookup_list)
        request = ('users/lookup',
                   {looking_by: lookup_list})
        return self.execute_api_call(request)

    def execute_api_call(self, request):
        """
        Take care of doing limit-respecting APl-calls.

        WARNING: Side effects: requests_processed, api_limits
        :param request: TwitterAPI formatted request tuple
        :return: list of requested objects
        """
        print('APIOps Api Limits: {}'.format(api_limits))
        if not self.limited(request[0]):
            global requests_processed, api_limits
            r = self.api.request(*request)
            requests_processed += 1
            self.set_api_limits(request[0], r.headers)
            my_return = self.process_api_request(r)
            return my_return
        print('APIOps Api Limits reached. Not executing until reset.')
        return False

    def set_api_limits(self, request_type, response_headers):
        """
        Update global API limits as received in responses.

        :param request_type: string
        :param response_headers: string
        """
        global api_limits
        api_limits[request_type] = \
            response_headers.get('x-rate-limit-remaining') or 1
        api_limits_reset[request_type] = \
            float(response_headers.get('x-rate-limit-reset')) or \
            calendar.timegm(time.gmtime())

    def process_api_request(self, r):
        """
        Put API response objects into a list
        :param r: API response object
        :return: list of objects from API response
        """
        output_container = []
        try:
            for item in r.get_iterator():
                output_container.append(item)
            return output_container
        except TwitterError.TwitterRequestError:
            return False