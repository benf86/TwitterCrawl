import glob
import re
import logging

import unidecode

import confighandler

logger = logging.getLogger('logger')


def get_filters():
    filter_list = \
        glob.glob('{}/*.filter'.format(confighandler.config['filterdir']))
    logger.info('Loading filters:\n{}'.format(filter_list))
    return filter_list


def get_filter_settings(filter_file):
    with open(filter_file) as my_filter_file:
        filter_content = my_filter_file.readlines()
    filter_settings = filter_content[0].strip()[:-1].split(';')
    filter_content = filter_content[1:]
    filter_content = \
        [clean_string(item)[:-1] for item in filter_content]
    return filter_settings, filter_content


def clean_string(my_string):
    return unidecode.unidecode(my_string.decode('utf-8').lower().strip())


def check(field, filter_content):
    result = any(i in field for i in filter_content)
    return result


class InfoProcessor():
    def __init__(self, user_object, dbhandler):
        self.config = confighandler.config
        self.filter_dir = self.config['filterdir']
        self.db_handler = dbhandler
        self.user = user_object
        self.user.name = unidecode.unidecode(unicode(self.user.name, 'utf-8'))

    def run_checks(self):
        results = None
        for filter_file in get_filters():
            filter_settings, filter_content = get_filter_settings(filter_file)
            checked_field = [self.user[filter_settings[0]]]
            if len(filter_settings) > 1:
                checked_field = filter_settings[0]
                for after_effect in filter_settings[1:]:
                    if after_effect[0] == '.':
                        checked_field = \
                            eval('"""{}"""{}()'.format(
                                clean_string(self.user[filter_settings[0]]),
                                after_effect))
                    else:
                        checked_field = \
                            eval('{aftereffect}("""{string}""")'
                                 .format(aftereffect=after_effect,
                                         string=clean_string(
                                             self.user[filter_settings[0]])))
            results = False or check(checked_field, filter_content)
        if results:
            self.accept_user()
        else:
            self.reject_user()

    def accept_user(self):
        print u'Accepted: @{}'.format(self.user.screen_name)
        self.db_handler.accept_user(self.user.id)

    def reject_user(self):
        print u'Rejected: @{}'.format(self.user.screen_name)
        self.db_handler.reject_user(self.user.id)
