class TwitterStatus():
    """
    Attributes from GET statuses/user_timeline:
    'contributors',
    'coordinates',
    'created_at',
    'entities',
    'favorite_count',
    'favorited',
    'geo',
    'id',
    'id_str',
    'in_reply_to_screen_name',
    'in_reply_to_status_id',
    'in_reply_to_status_id_str',
    'in_reply_to_user_id',
    'in_reply_to_user_id_str',
    'lang',
    'place',
    'possibly_sensitive',
    'retweet_count',
    'retweeted',
    'source',
    'text',
    'truncated',
    'user'
    """

    def __init__(self, status_dict):
        for key in status_dict:
            setattr(self, key, status_dict[key])

    def __str__(self):
        my_string = u'User: {user}\nRetweeted: {retweet_count}\n{text}' \
            .format(user=self.user['name'],
                    retweet_count=self.retweet_count,
                    text=self.text) \
            .encode('utf-8')
        return my_string