import calendar
import time

from time import gmtime, strftime

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
        print '\n{} Executing API request: {}' \
            .format(strftime("%Y-%m-%d %H:%M:%S", gmtime()), request[0])
        output_container = []
        r = self.api.request(*request)
        if r.headers.get('x-rate-limit-remaining') and \
                r.headers.get('x-rate-limit-limit'):
            print '\tWe have {}/{} {} API calls left before reset.' \
                .format(r.headers.get('x-rate-limit-remaining'),
                        r.headers.get('x-rate-limit-limit'),
                        request[0])
        for item in r.get_iterator():
            output_container.append(item)
        try:
            if any([r.headers.get('status') != '200 OK',
                    r.headers.get('x-rate-limit-remaining') == 0]):
                limit_reset_time = r.headers.get('x-rate-limit-reset')
                while not limit_reset_time:
                    r = self.api.request(*request)
                    limit_reset_time = float(
                        r.headers.get('x-rate-limit-reset'))
                sleep_duration_in_seconds = \
                    float(limit_reset_time) - float(
                        calendar.timegm(time.gmtime()))
                print 'API limit resets at {}. Sleeping until then... ZzZzzz' \
                    .format(strftime("%Y-%m-%d %H:%M:%S",
                                     gmtime(
                                         float(r.headers.get(
                                             'x-rate-limit-reset')))))
                time.sleep(sleep_duration_in_seconds)
        except KeyError as e:
            print 'KeyError exception: {}\nHeaders:\n{}'.format(e, r.headers)
        return output_container