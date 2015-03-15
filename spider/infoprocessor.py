import glob

import unidecode

import confighandler


def get_filters():
    filter_list = \
        glob.glob('{}/*.filter'.format(confighandler.config['filterdir']))
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
        results = []
        for filter_file in get_filters():
            filter_settings, filter_content = get_filter_settings(filter_file)
            checked_field = self.evaluate_filters(filter_settings)
            results.append(check(checked_field, filter_content))
        if any(results):
            self.accept_user()
        else:
            self.reject_user()

    def evaluate_filters(self, filter_settings):
        checked_field = clean_string(self.user[filter_settings[0]])
        if len(filter_settings) > 1:
            for after_effect in filter_settings[1:]:
                if after_effect[0] == '.':
                    checked_field = \
                        eval('"""{string}"""{aftereffect}()'.format(
                            string=checked_field.encode('string_escape'),
                            aftereffect=after_effect))
                else:
                    checked_field = \
                        eval('{aftereffect}("""{string}""")'
                             .format(aftereffect=after_effect,
                                     string=checked_field.encode(
                                         'string_escape')))
        return checked_field

    def accept_user(self):
        self.db_handler.accept_user(self.user.id)

    def reject_user(self):
        self.db_handler.reject_user(self.user.id)