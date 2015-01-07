import calendar
import time
import logging

from time import strftime, gmtime

from TwitterAPI import TwitterAPI

import confighandler

from crawlerhud import CrawlerHUD
from twitteruser import TwitterUser
from twitterstatus import TwitterStatus

logger = logging.getLogger('logger')

# API request limiting control values - remaining requests
api_limits = {'followers/ids': 1,
              'users/lookup': 1,
              'statuses/user_timeline': 1}
api_limits_reset = {'followers/ids': -1,
                    'users/lookup': -1,
                    'statuses/user_timeline': -1}
requests_processed = 0


class TwitterHandler():
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

    def get_followers_ids(self, screen_name):
        request = ('followers/ids',
                   {'screen_name': screen_name, 'count': 5000})
        return self.execute_api_call(request)

    def get_users_from_ids(self, user_id_list):
        output_container = []
        request = ()
        try:
            if user_id_list:
                # API call limited to 100 users at once
                user_id_list = user_id_list[0].get(u'ids')
                for ids in self.chunks(user_id_list, 100):
                    if ids:
                        csv_id_list = ",".join(map(str, ids))
                        request = ('users/lookup',
                                   {'user_id': csv_id_list})
                        response = self.execute_api_call(request)
                        if response:
                            output_container += response
                return output_container
        except Exception:
            logger.exception('\nuser_id_list: {}'
                             '\nrequest: {}'
                             '\nresponse: {}\n\n'.format(user_id_list,
                                                         request))

    def parse_users(self, user_list):
        if user_list:
            users = [TwitterUser(item) for item in user_list]
            return users

    def chunks(self, l, n):
        """ Yield successive n-sized chunks from l. """
        if l and n:
            for i in xrange(0, len(l), n):
                yield l[i:i + n]
        else:
            pass

    def get_statuses_from_ids(self, user_id_list):
        if user_id_list:
            output_container = {}
            for user_id in user_id_list:
                request = ('statuses/user_timeline',
                           {'user_id': user_id,
                            'count': 200,
                            'exclude_replies': 'true'})
                output_container[user_id] = \
                    self.execute_api_call(request)
            return output_container

    def parse_status(self, status):
        return TwitterStatus(status)

    def execute_api_call(self, request):
        global requests_processed, api_limits
        r = None

        def do_request():
            global requests_processed
            CrawlerHUD.hud('Request: {}'.format(request))
            r = self.api.request(*request)
            requests_processed += 1
            self.set_api_limits(request[0], r.headers)
            my_return = self.process_api_request(r)
            logger.debug('\n\nAPI REQUEST RETURNED\n\n{}'
                         .format(my_return))
            return my_return

        try:
            if int(api_limits[request[0]]) > 0:
                return do_request()
            else:
                self.check_reset_api_limits(request[0])
                return do_request()
        except Exception:
            if not r:
                r.headers = 'Crash before request processed'
            logger.exception(
                '\nRequest that triggered the exception:\n{}\n\nResponse '
                'headers that triggered the exception:\n{}'.format(
                    request, r.headers))

    def set_api_limits(self, request_type, request_headers):
        global api_limits
        api_limits[request_type] = \
            request_headers.get('x-rate-limit-remaining') or 1
        api_limits_reset[request_type] = \
            float(request_headers.get('x-rate-limit-reset')) or \
            calendar.timegm(time.gmtime())

    def check_reset_api_limits(self, request_type):
        global api_limits_reset
        cur_time = calendar.timegm(time.gmtime())
        reset_time = float(api_limits_reset[request_type])
        if reset_time >= cur_time:
            sleep_duration_in_seconds = \
                reset_time - cur_time + 5
            CrawlerHUD.hud('Status: {} sleeping until {}'
                           .format(request_type,
                                   strftime("%H:%M:%S",
                                            gmtime(reset_time))))
            logger.info('Status: {} sleeping until {}'
                        .format(request_type,
                                strftime("%H:%M:%S",
                                         gmtime(reset_time))))
            time.sleep(sleep_duration_in_seconds)
            CrawlerHUD.hud('Status: {} waking up'.format(request_type))
            logger.info('Status: {} waking up'.format(request_type))
        for k, v in api_limits_reset.iteritems():
            if v < cur_time:
                api_limits[k] = -1

    def process_api_request(self, r):
        output_container = []
        for item in r.get_iterator():
            output_container.append(item)
        return output_container