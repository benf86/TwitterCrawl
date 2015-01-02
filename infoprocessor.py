import re

import unidecode


with open('./filters/names.csv') as names_file, \
        open('./filters/surnames.csv') as surnames_file:
    names = [unidecode.unidecode(line.decode('utf-8').lower().strip()[:-1])
             for line in names_file.readlines()] + \
            [unidecode.unidecode(line.decode('utf-8').lower().strip()[:-1])
             for line in surnames_file.readlines()]

with open('./filters/settlements.csv') as locations_file:
    locations = set(
        unidecode.unidecode(line.decode('utf-8').lower().strip()[:-1])
        for line in locations_file.readlines())


class InfoProcessor():
    def __init__(self, user_object, dbhandler):
        self.db_handler = dbhandler
        self.user = user_object
        self.names = names
        self.locations = locations
        self.user.name = unidecode.unidecode(unicode(self.user.name, 'utf-8'))

    def check_name(self):
        split_name = self.user.name.split()
        if len(split_name) == 2:
            if (split_name[0] in self.names) or \
                    (split_name[1] in self.names):
                return True
        elif len(split_name) == 1:
            if split_name[0] in self.names:
                return True
        return False

    def check_location(self):
        split_location = re.findall(r'[\w]+', self.user.location.lower())
        if any(i in split_location for i in
               ['slovenia', 'slovenija', 'si', '.si']):
            return True
        return any(i in split_location for i in self.locations)

    def check_language(self):
        if 'sl' in self.user.lang:
            return True
        return False

    def run_checks(self):
        #print 'Checking name: {}'.format(self.user.name)
        accepted = self.check_name()
        #print 'Checking language: {}'.format(self.user.lang)
        accepted = accepted or self.check_language()
        #print 'Checking location: {}'.format(self.user.location)
        accepted = accepted or self.check_location()
        if accepted:
            self.accept_user()
        else:
            self.reject_user()

    def accept_user(self):
        print u'Accepted: @{}'.format(self.user.screen_name)
        self.db_handler.accept_user(self.user.id)

    def reject_user(self):
        print u'Rejected: @{}'.format(self.user.screen_name)
        self.db_handler.reject_user(self.user.id)
