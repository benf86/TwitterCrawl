from sqlalchemy import Column, BigInteger, String, Text, Enum, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

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
    proc_status = Column(
        Enum('raw', 'enqueued', 'accepted', 'rejected', name='proc_status'))
    been_followed = Column(
        Enum('followed', 'not_followed', 'processing', name='been_followed'),
        nullable=False)
    deep_checked = Column(Boolean, nullable=False)  # were the tweets regex'd?


engine = create_engine(
    'postgresql://{dbuser}:{dbpass}@{dbhost}:{dbport}/{db}'.format(**config))

Base.metadata.create_all(engine)