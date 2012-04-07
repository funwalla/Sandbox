# -*- coding: utf-8 -*-

"""Provides functions to fetch Twitter keys from the Redis key store.

Functions provided:
get_twitter_consumer_key()
get_twitter_consumer_secret()
get_twitter_oauth_token()
get_twitter_oauth_token_secret()
"""

import redis

redis = redis.Redis()
keys = redis.hgetall('twitter_keys')

def get_twitter_consumer_key():
    """Returns the Twitter consumer key as a string.
    Accepts no agurments"""
    return keys['consumer_key']

def get_twitter_consumer_secret():
    """Returns the Twitter consumer secret as a string,
    Accepts no agruments."""
    return keys['consumer_secret']

def get_twitter_oauth_token():
    """Returns the Twitter oauth token as a string.
    Accepts no arguments."""
    return keys['oauth_token']

def get_twitter_oauth_token_secret():
    """Returns the Twitter oauth token secret as a string.
    Accepts no arguments"""
    return keys['oauth_token_secret']


if __name__ == "__main__":
    
    print "Redis returned the following Twitter keys:"
    print "consumer_key:", get_twitter_consumer_key()
    print "consumer_secret:", get_twitter_consumer_secret()
    print "oauth_token:", get_twitter_oauth_token()
    print "oauth_token_secret:", get_twitter_oauth_token_secret()
