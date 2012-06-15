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
    
    logging.debug("entering")
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
            logging.warning("URLError encountered. Continuing.")
            if error_count > max_errors:
                logging.warning("Too many consecutive errors: bailing out.")
                raise

def _getRemainingHits(t):
    logging.debug("entering")
    return t.account.rate_limit_status()['remaining_hits']

# Handle the common HTTPErrors. 
# Return an updated value for wait_period if the problem is a 503 error.
# Block until the rate limit is reset if a rate limiting issue.
def handleTwitterHTTPError(e, t, wait_period=2):

    logging.debug("entering")
    if wait_period > 3600: #seconds
        logging.warning("Too many retries: quitting.")
        raise e

    if e.e.code == 401:
        logging.warning("Encountered 401 Error (Not Authorized)")
        return None
    elif e.e.code in (502, 503):
        logging.warning("Encountered %i Error. Will return in %i seconds", \
                     e.e.code, wait_period)
        time.sleep(wait_period)
        wait_period *= 1.5
        return wait_period
    elif (_getRemainingHits(t) == 0 or e.e.code == 400):
        status = t.account.rate_limit_status()
        now = time.time()  #UTC
        when_rate_limit_resets = status['reset_time_in_seconds']
        logging.debug("Rate limit reached: reset_time_in_seconds = ",
                      when_rate_limit_resets)
        #Prevent negative numbers
        sleep_time = max(when_rate_limit_resets - now, 5)
        
        logging.warning("Rate limit reached: sleeping for %i seconds.", sleep_time)
        time.sleep(sleep_time)
        return 2  # used to reset wait_period to 2 seconds.
    else:
        raise e

# A template-like function that can get friends or followers depending on 
# the function passed into it via func. Stores results in a redis set with
# key 'screen_name$' + f_screen_name + '$' + key_name
# 
def _getFriendsOrFollowersUsingFunc(func, key_name, twitterConnection, redisConnection,
                                    screen_name=None, limit=FRIENDS_LIMIT):
    
    logging.debug("entering")
    cursor = -1

    result = []
    result_count = 0
    while cursor != 0:
        logging.debug("while loop: cursor = %d", cursor)
        response = makeTwitterRequest(twitterConnection, func,
                                      screen_name=screen_name, cursor=cursor)
        logging.debug("got %d responses", len(response))
        for _id in response['ids']:
            logging.debug("response id for loop, _id = %s", _id)
            result.append(_id)
            redisConnection.sadd(getRedisIdByScreenName(screen_name, key_name),
                                 _id)
        cursor = response['next_cursor']
        result_count += len(response['ids'])
        scard = redisConnection.scard(getRedisIdByScreenName(screen_name, key_name))
        logging.debug("Fetched %s ids for %s", scard, screen_name)
        #if scard >= limit:
        if result_count >= limit:
            break

    return result

# Stores user info in redis sets keyed by screen_name and user id
# i.e.: 'screen_name$' + screen_name/user_id + '$info.json'
def getUserInfo(twitterConnection, redisConnection, screen_names=[], user_ids=[],
                verbose=False, sample=1.0):

    logging.debug("entering")
    # Sampling technique: randomize the lists and trim the length.

    if sample < 1.0:
        for lst in [screen_names, user_ids]:
            shuffle(lst)
            lst = lst[:int(len(lst) * sample)]

    logging.info("Retrieving user info for %d screen names and %d user ids",
                 len(screen_names), len(user_ids) )
    
    info = []
    while len(screen_names) > 0:
        logging.debug("screen_name while loop: Found %d screen names", len(screen_names))
        screen_names_str = ','.join(screen_names[:100])
        screen_names = screen_names[100:]
        logging.debug("%s", screen_names_str)

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
        logging.info("Completed user info search for %d screen names", len(info) )

    while len(user_ids) > 0:
        logging.debug("user id while loop: found %d user ids", len(user_ids))
        user_ids_str = ','.join([str(_id) for _id in user_ids[:100]])
        logging.debug("%s", user_ids_str)
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
        logging.debug("Completed user info search for %d user ids", len(info) )

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