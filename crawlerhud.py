import os
from time import strftime, gmtime
from collections import deque

import twitterhandler

last_action = deque([])


class CrawlerHUD():
    def __init__(self):
        pass

    @staticmethod
    def hud(current_action=''):
        global last_action
        if current_action:
            last_action.append('{}\t{}...'.format(strftime("%H:%M:%S",
                                                           gmtime()),
                                                  current_action[:60]))
        os.system(['clear', 'cls'][os.name == 'nt'])
        print 'API calls made so far: {}' \
            .format(twitterhandler.requests_processed)
        print '{:25}| {:10}{}'.format('Request', '# left', 'resets at')
        print '_' * 56
        for k, v in twitterhandler.api_limits.iteritems():
            print '{key:25}| {status:10}{reset_time}' \
                .format(key=k, status=v,
                        reset_time=strftime("%H:%M:%S",
                                            gmtime(float(twitterhandler
                                                .api_limits_reset[k]))))
        print '_' * 56
        print '\nHistory:'
        for action in last_action:
            print action
        if len(last_action) > 10:
            last_action.popleft()