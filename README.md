(In the process of being rewritten in the rewrite branch)

A Twitter crawler/scraper, which builds a Twitter user database based on certain filters

For testing/use, run generatetables.py first. Then run worker.py or crawler.py to generate the config file. Fill it out and run both for the fun to begin.

Filters are handled in/by infoprocessor.py, which automatically reads all filter files in the filter directory (default ./filters).

Check the supplied filters to see the format. Generally, first row includes the name of the TwitterUser field to check against values in the rest of the file (one per line, ending with a comma), which is optionally followed by one or more functions to perform on the field value before filtering, preceded by a semicolon. Note that the format is .function for functions that don't take an argument and function (w/o the dot) for functions where the value is the argument. Parentheses are omitted in either case.
E.g. '.lower' or 'int' for 'x.lower()' and 'int(x)' respectively.

The initial user name(s) go in the file seed.txt.

Dependencies:
* sqlalchemy
* pika
* TwitterAPI
* unidecode
* PostgreSQL
* RabbitMQ
