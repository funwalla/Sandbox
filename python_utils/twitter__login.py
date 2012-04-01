# -*- coding: utf-8 -*-

"""Provides the function login() for Twitter

Uses the get_twitter_keys module to login in to Twitter and
return a twitter.Twitter object on the api.twitter.com domain"""

import os
import twitter
import get_twitter_keys as tkeys

def login():
    """Provides a Twitter object reference
    
    Arguments: none.
    
    Return value: A twitter.Twitter object on the api.twitter.com domain.
    
    Restrictions: requires the get_twitter_keys module which in turn
    requires a Redis keystore.
    """
    
    CONSUMER_KEY = tkeys.get_twitter_consumer_key()
    CONSUMER_SECRET = tkeys.get_twitter_consumer_secret()
    OAUTH_TOKEN = tkeys.get_twitter_oauth_token()
    OAUTH_TOKEN_SECRET = tkeys.get_twitter_oauth_token_secret()
    
    return twitter.Twitter(domain='api.twitter.com', api_version='1',
                           auth=twitter.OAuth(OAUTH_TOKEN,
                                              OAUTH_TOKEN_SECRET,
                                              CONSUMER_KEY,
                                              CONSUMER_SECRET))

if __name__ == '__main__':
    login()

