# -*- coding: utf-8 -*-
"""
Crawl down one level for each friend and follower of the input screen_names
and return the user info. The program expect the input screen_names as
command-line arguments.
"""

import sys
import redis
import functools
import time
import logging
from twitter__login import login
from twitter__util import getUserInfo
from twitter__util import _getFriendsOrFollowersUsingFunc

SCREEN_NAME = sys.argv[1]

# Comment out the following line to enable logging.
#logging.disable(logging.INFO)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:%(module)s:%(lineno)d:'\
                    '%(funcName)s:%(levelname)s: %(message)s')

t = login()
r = redis.Redis()

logging.info('Started crawler')


# Some wrappers around _getFriendsOrFollowersUsingFunc that 
# create convenience functions

# Stores results is a redis set with key
#'screen_name$' + friend_screen_name + '$friend_ids'
getFriends = functools.partial(_getFriendsOrFollowersUsingFunc, 
                               t.friends.ids, 'friend_ids', t, r)

# Stores results is a redis set with key
#'screen_name$' + follower_screen_name + '$follower_ids'
getFollowers = functools.partial(_getFriendsOrFollowersUsingFunc,
                                 t.followers.ids, 'follower_ids', t, r)

def crawl(
    screen_names,
    friends_limit=10000,
    followers_limit=10000,
    depth=1,
    friends_sample=0.2, #XXX
    followers_sample=0.0,
    ):

    logging.info("Getting user info")
    getUserInfo(t, r, screen_names=screen_names)
    for screen_name in screen_names:
        
        logging.info("Getting friends ids")
        friend_ids = getFriends(screen_name, limit=friends_limit)
        
        logging.info("Getting follower ids")
        follower_ids = getFollowers(screen_name, limit=followers_limit)

        logging.info("Getting friends info")
        friends_info = getUserInfo(t, r, user_ids=friend_ids, 
                                   sample=friends_sample)

        logging.info("Getting follower info")
        followers_info = getUserInfo(t, r, user_ids=follower_ids,
                                     sample=followers_sample)

        next_queue = [u['screen_name'] for u in friends_info + followers_info]

        d = 1
        while d < depth:
            logging.info("while loop: depth = %d, d = %d", depth, d)
            d += 1
            (queue, next_queue) = (next_queue, [])
            for _screen_name in queue:
                logging.info("while loop: screen_name: %s:", _screen_name)
                friend_ids = getFriends(_screen_name, limit=friends_limit)
                follower_ids = getFollowers(_screen_name, limit=followers_limit)

                next_queue.extend(friend_ids + follower_ids)

                # Note that this function takes a kw between 0.0 and 1.0 called
                # sample that allows you to crawl only a random sample of nodes
                # at any given level of the graph
                logging.info("while loop: getting user info")
                getUserInfo(user_ids=next_queue)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Please supply at least one screen name."
    else:
        logging.info("Crawling for: %s", SCREEN_NAME)
        crawl([SCREEN_NAME])
        logging.info("Crawl completed")
        
        # The data is now in the system. Do something interesting. For example, 
        # find someone's most popular followers as an indiactor of potential influence.
        # See friends_followers__calculate_avg_influence_of_followers.py

        print "Crawl completed"
        print "\nFriend/Follower ids for each input_screen_name are given in redis keys"
        print "screen_name$input_screen_name$friend/follower_ids"
        print "\nUser info for each friend and follower is given in redis keys:"
        print "screen_name$friend/follower_screen_name$info.json"
        print "and user_id$friend/follower_id$info.json"
