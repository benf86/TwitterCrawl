# -*- coding: utf-8 -*-
"""
This module takes care of TWs API operations.
"""
import calendar
from datetime import time
from pprint import pprint

from TwitterAPI import TwitterAPI

import confighandler


# API request limiting control values - remaining requests
api_limits = {'followers/ids': 1,
              'users/lookup': 1,
              'statuses/user_timeline': 1}
api_limits_reset = {'followers/ids': -1,
                    'users/lookup': -1,
                    'statuses/user_timeline': -1}
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
        global requests_processed, api_limits
        r = None

        print('\n\nExecuting new API call:\n_________________________________')

        def do_request():
            """
            Execute the request and return list of requested objects
            :return: list of objects or single object
            """
            global requests_processed
            r = self.api.request(*request)
            requests_processed += 1
            self.set_api_limits(request[0], r.headers)
            my_return = self.process_api_request(r)
            print('APIOps Api Limits: {}'.format(api_limits))
            print('APIOps Response:')
            pprint(my_return)
            return my_return

        print('APIOps Request: {}'.format(request))
        try:
            """Check API Limits"""
            if int(api_limits[request[0]]) > 0:
                return do_request()
            else:
                self.check_reset_api_limits(request[0])
                return do_request()
        except Exception:
            if not r:
                r.headers = 'Crash before request processed'
            print('\nAPI Ops Exception: Request that triggered the exception:\
                \n{}\n\nResponse headers that triggered the exception:\n{}'
                  .format(request, r.headers))

    def set_api_limits(self, request_type, request_headers):
        """
        Update global API limits as received in responses.

        :param request_type: string
        :param request_headers: string
        """
        global api_limits
        api_limits[request_type] = \
            request_headers.get('x-rate-limit-remaining') or 1
        api_limits_reset[request_type] = \
            float(request_headers.get('x-rate-limit-reset')) or \
            calendar.timegm(time.gmtime())

    def check_reset_api_limits(self, request_type):
        """
        Check if API request limits have been reached for a specific type.
        :param request_type: string
        """
        global api_limits_reset
        cur_time = calendar.timegm(time.gmtime())
        reset_time = float(api_limits_reset[request_type])
        if reset_time >= cur_time:
            sleep_duration_in_seconds = \
                reset_time - cur_time + 5
            time.sleep(sleep_duration_in_seconds)
        for k, v in api_limits_reset.iteritems():
            if v < cur_time:
                api_limits[k] = -1

    def process_api_request(self, r):
        """
        Put API response objects into a list
        :param r: API response object
        :return: list of objects from API response
        """
        output_container = []
        for item in r.get_iterator():
            output_container.append(item)
        return output_container