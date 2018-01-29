# coding: utf-8

import json

class Config:
    """Class that contains all  config variables. It loads user values from a json file """

    # Default values
    consumer_key = None
    consumer_secret = None
    access_token_key = None
    access_token_secret = None
    daily_tweets = 300
    scan_update_time = 5400
    clear_queue_time = 43200
    min_posts_queue = 60
    rate_limit_update_time = 60
    blocked_users_update_time = 300
    min_ratelimit = 10
    min_ratelimit_retweet = 20
    min_ratelimit_search = 40
    max_follows = 1950
    search_queries = ["RT to win", "Retweet and win"]
    follow_keywords = [" follow ", " follower "]
    fav_keywords = [" fav ", " favorite ", "like"]

    @staticmethod
    def load(filename):
        # Load our configuration from the JSON file.
        with open(filename) as data_file:
            data = json.load(data_file)

        for key, value in data.items():
            #!Fixme:
            #Hacky code because the corresponding keys in config file use - instead of _
            key = key.replace('-', '_')
            setattr(Config, key, value)
