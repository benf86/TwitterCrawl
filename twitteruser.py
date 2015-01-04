class TwitterUser():
    """
    Attributes from GET users/lookup:
    'contributors_enabled',
    'created_at',
    'default_profile',
    'default_profile_image',
    'description',
    'entities',
    'favourites_count',
    'follow_request_sent',
    'followers_count',
    'following',
    'friends_count',
    'geo_enabled',
    'id',
    'id_str',
    'is_translation_enabled',
    'is_translator',
    'lang',
    'listed_count',
    'location',
    'name',
    'notifications',
    'profile_background_color',
    'profile_background_image_url',
    'profile_background_image_url_https',
    'profile_background_tile',
    'profile_banner_url',
    'profile_image_url',
    'profile_image_url_https',
    'profile_link_color',
    'profile_location',
    'profile_sidebar_border_color',
    'profile_sidebar_fill_color',
    'profile_text_color',
    'profile_use_background_image',
    'protected',
    'screen_name',
    'status',
    'statuses_count',
    'time_zone',
    'url',
    'utc_offset',
    'verified'
    """

    def __init__(self, user_dict={}):
        for key in user_dict:
            setattr(self, key, user_dict[key])

    def __getitem__(self, item):
        return getattr(self, item)

    def __str__(self):
        my_string = unicode('User: {user}\nusername: {screen_name}\nid: {' \
                            'id}\nLocation: {location}\n' \
                            'Language: {lang}\nFollowers: {followers}' \
                            .format(user=self.name,
                                    screen_name=self.screen_name,
                                    id=str(self.id),
                                    location=self.location,
                                    followers=str(self.followers_count),
                                    lang=self.lang), 'utf-8')
        return my_string