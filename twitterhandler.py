import calendar
import time

from TwitterAPI import TwitterAPI

from twitteruser import TwitterUser
from twitterstatus import TwitterStatus


class TwitterHandler():
    def __init__(self, config):
        self.config = config
        self.api_key = self.config['twapikey']
        self.api_secret = self.config['twapisecret']
        self.access_token = self.config['twaccess']
        self.access_token_secret = self.config['twaccesssecret']
        self.api = TwitterAPI(self.api_key,
                              self.api_secret,
                              self.access_token,
                              self.access_token_secret)

    def get_followers_ids(self, screen_name):
        request = ('followers/ids',
                   {'screen_name': screen_name, 'count': 5000})
        return self.execute_api_call_and_sleep_if_limit_reached(request)

    def get_users_from_ids(self, user_id_list):
        output_container = []
        # API call limited to 100 users at once
        for ids in self.chunks(user_id_list[0][u'ids'], 100):
            csv_id_list = ",".join(map(str, ids))
            request = ('users/lookup',
                       {'user_id': csv_id_list})
            output_container += \
                self.execute_api_call_and_sleep_if_limit_reached(request)
        return output_container

    def parse_users(self, user_list):
        users = [TwitterUser(item) for item in user_list]
        return users

    def chunks(self, l, n):
        """ Yield successive n-sized chunks from l. """
        for i in xrange(0, len(l), n):
            yield l[i:i + n]

    def get_statuses_from_ids(self, user_id_list):
        output_container = []
        for user_id in user_id_list:
            request = ('statuses/user_timeline',
                       {'user_id': user_id,
                        'count': 200,
                        'exclude_replies': 'true'})
            output_container += \
                self.execute_api_call_and_sleep_if_limit_reached(request)
        return output_container

    def parse_statuses(self, status_list):
        statuses = [TwitterStatus(item) for item in status_list]
        return statuses

    def execute_api_call_and_sleep_if_limit_reached(self, request):
        print 'Executing API request: {}'.format(request[0])
        output_container = []
        r = self.api.request(*request)
        for item in r.get_iterator():
            output_container.append(item)
        try:
            if any([r.headers.get('status') != '200 OK',
                    r.headers.get('x-rate-limit-remaining') == 0]):
                limit_reset_time = r.headers.get('x-rate-limit-reset')
                while not limit_reset_time:
                    r = self.api.request(*request)
                    limit_reset_time = int(r.headers.get('x-rate-limit-reset'))
                sleep_duration_in_seconds = \
                    limit_reset_time - calendar.timegm(time.gmtime())
                print 'API limit resets in {} seconds' \
                    .format(sleep_duration_in_seconds)
                time.sleep(sleep_duration_in_seconds)
        except KeyError as e:
            print 'KeyError exception: {}\nHeaders:\n{}'.format(e, r.headers)
        return output_container