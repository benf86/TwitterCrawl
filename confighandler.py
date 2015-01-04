import os
import logging
import sys

logger = logging.getLogger('logger')

config = {}
configFilePath = "{}/config.txt".format(
    os.path.dirname(os.path.realpath(
        __file__)))


def check_config_exists():
    read_config_from_disk()
    if not check_config_keys():
        generate_config()
        write_config_to_disk()
    return config


def read_config_from_disk():
    global config
    print 'Trying to read config file...'
    try:
        with open(configFilePath, "r") as my_config:
            for line in my_config:
                (key, val) = line.strip().split("=")
                config[key] = val
        print 'Config file successfully read!'
        return True
    except IOError as e:
        print 'Config file cannot be accessed: {}'.format(e)
        logger.exception('\n')
    except Exception as e:
        logger.exception('\n')
    return False


def check_config_keys():
    config_fields = ['db', 'dbuser', 'dbpass', 'dbhost', 'dbport', 'dbtable',
                     'rabbithost', 'rabbitqueue', 'twapikey', 'twapisecret',
                     'twaccess', 'twaccesssecret', 'filterdir']

    return sorted(config.keys()) == sorted(config_fields)


def generate_config():
    global config
    config = {
        "db": "om5000",
        "dbuser": "",
        "dbpass": "",
        "dbhost": "localhost",
        "dbport": "5432",
        "dbtable": "users",
        "rabbithost": "localhost",
        "rabbitqueue": "om5000",
        "twapikey": "",
        "twapisecret": "",
        "twaccess": "",
        "twaccesssecret": "",
        "filterdir": "./filters"
    }
    return config


def write_config_to_disk():
    try:
        with open(configFilePath, "w") as my_config:
            for key in sorted(config):
                my_config.write("%s=%s\n" % (key, config[key]))
        print 'Please edit the config with correct values at: {}' \
            .format("{}/config.txt".format(
            os.path.dirname(os.path.realpath(__file__))))
        sys.exit(0)
    except Exception as e:
        logger.exception('\n')
        return False


check_config_exists()
