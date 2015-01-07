import os
from time import strftime, gmtime, sleep
from collections import deque

import dbhandler

last_action = deque([])
accepted = 0
total = 0
queued = 0
with_tweets = 0


class WorkerHUD():
    def __init__(self):
        pass

    @staticmethod
    def hud(current_action=''):
        global last_action, accepted, total, with_tweets
        if current_action:
            last_action.append('{}\t{}'.format(strftime("%H:%M:%S", gmtime()),
                                               current_action))
        os.system(['clear', 'cls'][os.name == 'nt'])
        print '{:25}| {accepted}/{total}'.format('Accepted users in database',
                                                 accepted=accepted,
                                                 total=total)
        print '{:25}| {queued}'.format('Queued for processing',
                                       queued=queued)
        print '{:25}| {with_tweets}'.format('Accepted users with tweets',
                                            with_tweets=with_tweets)
        print '_' * 56
        print '\nHistory:'
        for action in last_action:
            print action
        if len(last_action) > 10:
            last_action.popleft()

    @staticmethod
    def update_hud_data():
        while True:
            global total, accepted, queued, with_tweets
            with dbhandler.DBHandler() as db:
                db.execute('SELECT COUNT(*) FROM users')
                total = db.fetchone()[0]
                db.execute(
                    'SELECT COUNT(*) FROM users WHERE proc_status = '
                    '\'accepted\'')
                accepted = db.fetchone()[0]
                db.execute(
                    'SELECT COUNT(*) FROM users WHERE proc_status = '
                    '\'accepted\' '
                    'AND tweets != \'\'')
                with_tweets = db.fetchone()[0]
                db.execute(
                    'SELECT COUNT(*) FROM users WHERE proc_status = '
                    '\'enqueued\'')
                queued = db.fetchone()[0]
            sleep(10)