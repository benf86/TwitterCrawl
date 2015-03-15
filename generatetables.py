from sqlalchemy import Column, BigInteger, String, Text, Enum, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

import dbops

import confighandler


Base = declarative_base()
config = confighandler.config


class Users(Base):
    __tablename__ = config['dbtable']
    # twitter id
    id = Column(BigInteger(), unique=True, index=True, primary_key=True)
    screen_name = Column(String(15), nullable=False, unique=True)
    description = Column(Text(), nullable=True)
    followers_count = Column(BigInteger(), nullable=False)  # followers
    friend = Column(BigInteger(), nullable=False)  # is follower of
    lang = Column(Text(), nullable=False)
    location = Column(Text(), nullable=True)
    name = Column(Text(), nullable=True)
    tweets = Column(Text(), nullable=True)
    proc_status = Column(
        Enum('raw', 'enqueued', 'accepted', 'rejected', name='proc_status'))
    been_followed = Column(
        Enum('followed', 'not_followed', 'processing', name='been_followed'),
        nullable=False)
    deep_checked = Column(Boolean, nullable=False)  # were the tweets regex'd?


def add_db_rule_ignore_duplicates(tables_list):
    """
    Add the PostgreSQL rule to skip duplicate entries.
    """
    with dbops.DBOps() as cur:
        try:
            for table in tables_list:
                cur.execute(
                    'SELECT * FROM pg_rules '
                    'WHERE rulename = \'on_duplicate_ignore\'')
                if not cur.fetchone():
                    cur.execute(
                        'CREATE RULE "on_duplicate_ignore" AS ON INSERT '
                        'TO "{'
                        'table}" '
                        'WHERE EXISTS(SELECT 1 FROM {table} WHERE '
                        'id=NEW.id) '
                        'DO INSTEAD NOTHING;'.format(table=table))
        except Exception:
            cur.rollback()
            raise


engine = create_engine(
    'postgresql://{dbuser}:{dbpass}@{dbhost}:{dbport}/{db}'.format(**config))

Base.metadata.create_all(engine)
add_db_rule_ignore_duplicates(['users'])

