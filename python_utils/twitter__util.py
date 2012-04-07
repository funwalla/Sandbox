# -*- coding: utf-8 -*-

import sys
import locale
import twitter
import redis
import json
import time
import logging
from random import shuffle
from urllib2 import URLError
from twitter__login import login

FRIENDS_LIMIT = 10000

def makeTwitterRequest(t, twitterFunction, max_errors=3, *args, **kwArgs):
    
    logging.info("entering")
    wait_period = 2
    error_count = 0
    
    while True:
        try:
            return twitterFunction(*args, **kwArgs)
        except twitter.api.TwitterHTTPError, e:
            error_count = 0
            wait_period = handleTwitterHTTPError(e, t, wait_period)
            if wait_period is None:
                return
        except URLError, e:
            error_count += 1
            logging.info("URLError encountered. Continuing.")
            if error_count > max_errors:
                logging.info("Too many consecutive errors: bailing out.")
                raise

def _getRemainingHits(t):
    logging.info("entering")
    return t.account.rate_limit_status()['remaining_hits']

# Handle the common HTTPErrors. 
# Return an updated value for wait_period if the problem is a 503 error.
# Block until the rate limit is reset if a rate limiting issue.
def handleTwitterHTTPError(e, t, wait_period=2):

    logging.info("entering")
    if wait_period > 3600: #seconds
        logging.info("Too many retries: quitting.")
        raise e

    if e.e.code == 401:
        logging.info("Encountered 401 Error (Not Authorized)")
        return None
    elif e.e.code in (502, 503):
        logging.info("Encountered %i Error. Will return in %i seconds", \
                     e.e.code, wait_period)
        time.sleep(wait_period)
        wait_period *= 1.5
        return wait_period
    elif _getRemainingHits(t) == 0:
        status = t.account.rate_limit_status()
        now = time.time()  #UTC
        when_rate_limit_resets = status['reset_time_in_seconds']
        #Prevent negative numbers
        sleep_time = max(when_rate_limit_resets - now, 5)
        
        logging.info("Rate limit reached: sleeping for %i seconds.", sleep_time)
        time.sleep(sleep_time)
        return 2  # used to reset wait_period to 2 seconds.
    else:
        raise e

# A template-like function that can get friends or followers depending on 
# the function passed into it via func
def _getFriendsOrFollowersUsingFunc(func, key_name, twitterConnection, redisConnection,
                                    screen_name=None, limit=FRIENDS_LIMIT):
    
    logging.info("entering")
    cursor = -1

    result = []
    while cursor != 0:
        logging.info("while loop: cursor = %d", cursor)
        response = makeTwitterRequest(twitterConnection, func,
                                      screen_name=screen_name, cursor=cursor)
        logging.info("got %d responses", len(response))
        for _id in response['ids']:
            logging.info("response id for loop, _id = %s", _id)
            result.append(_id)
            redisConnection.sadd(getRedisIdByScreenName(screen_name, key_name),
                                 _id)
        cursor = response['next_cursor']
        scard = redisConnection.scard(getRedisIdByScreenName(screen_name, key_name))
        logging.info("Fetched %s ids for %s", scard, screen_name)
        if scard >= limit:
            break

    return result

def getUserInfo(twitterConnection, redisConnection, screen_names=[], user_ids=[],
                verbose=False, sample=1.0):

    logging.info("entering")
    # Sampling technique: randomize the lists and trim the length.

    if sample < 1.0:
        for lst in [screen_names, user_ids]:
            shuffle(lst)
            lst = lst[:int(len(lst) * sample)]

    info = []
    while len(screen_names) > 0:
        logging.info("screen_name while loop: Found %d screen names", len(screen_names))
        screen_names_str = ','.join(screen_names[:100])
        screen_names = screen_names[100:]
        logging.info("%s", screen_names_str)

        response = makeTwitterRequest(twitterConnection,
                                      twitterConnection.users.lookup,
                                      screen_name=screen_names_str)
        if response is None:
            break
        if type(response) is dict:  # handle api quirk
            response = [response]

        for user_info in response:
            redisConnection.set(getRedisIdByScreenName(user_info['screen_name'],
                                                       'info.json'),
                                json.dumps(user_info))
            redisConnection.set(getRedisIdByUserId(user_info['id'],
                                                   'info.json'),
                                json.dumps(user_info))
        info.extend(response)

    while len(user_ids) > 0:
        logging.info("user id while loop: found %d user ids", len(user_ids))
        user_ids_str = ','.join([str(_id) for _id in user_ids[:100]])
        logging.info("%s", user_ids_str)
        user_ids = user_ids[100:]

        response = makeTwitterRequest(twitterConnection, 
                                      twitterConnection.users.lookup,
                                      user_id=user_ids_str)


        if response is None:
            break

        if type(response) is dict:  # Handle api quirk
            response = [response]
        for user_info in response:
            redisConnection.set(getRedisIdByScreenName(user_info['screen_name'], 'info.json'),
                                json.dumps(user_info))
            redisConnection.set(getRedisIdByUserId(user_info['id'], 'info.json'), 
                                json.dumps(user_info))
        info.extend(response)         

    return info

# Covenience functions

def pp(_int):  # For nice number formatting
    locale.setlocale(locale.LC_ALL, '')
    return locale.format('%d', _int, True)


def getRedisIdByScreenName(screen_name, key_name):
    return 'screen_name$' + screen_name + '$' + key_name


def getRedisIdByUserId(user_id, key_name):
    return 'user_id$' + str(user_id) + '$' + key_name


if __name__ == '__main__': # For ad-hoc testing

    def makeTwitterRequest(t, twitterFunction, *args, **kwArgs): 
        wait_period = 2
        while True:
            try:
                e = Exception()
                e.code = 401
                #e.code = 502
                #e.code = 503
                raise twitter.api.TwitterHTTPError(e, "http://foo.com", "FOO", "BAR")
                return twitterFunction(*args, **kwArgs)
            except twitter.api.TwitterHTTPError, e:
                wait_period = handleTwitterHTTPError(e, t, wait_period)
                if wait_period is None:
                    return

    def _getRemainingHits(t):
        return 0

    t = login()
    makeTwitterRequest(t, t.friends.ids, screen_names=['SocialWebMining'])