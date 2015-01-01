A Twitter crawler/scraper, which builds a Twitter user database based on certain filters

For testing/use, run generatetables.py first. Upon first run of main.py, the config file will be created. Fill it with required settings and re-run main.py.

Filters are handled in/by infoprocessor.py.

The initial user name(s) are in the file seed.txt.

Dependencies:
* sqlalchemy
* pika
* TwitterAPI
* unidecode
* PostgreSQL
* RabbitMQ
