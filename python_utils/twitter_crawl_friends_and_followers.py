# -*- coding: utf-8 -*-
"""
Crawl down one level for each friend and follower of the input screen_names
and return the user info. The program expect the input screen_names as
command-line arguments. Enclose multiple screen names in single or double quotes
example: "Tom Dick Harry"

From example 4-8 of MtSW
"""

import sys
import redis
import functools
import time
import logging
from twitter__login import login
from twitter__util import getUserInfo
from twitter__util import _getFriendsOrFollowersUsingFunc

SCREEN_NAMES_LIST = sys.argv[1].split()

#logging.disable(logging.DEBUG)

logging.basicConfig(level=logging.DEBUG,
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
    followers_limit=100000,
    depth=1,
    friends_sample=0.2, #XXX
    followers_sample=0.2,
    ):

    logging.info("Getting user info")
    getUserInfo(t, r, screen_names=screen_names)
    for screen_name in screen_names:
        
        friend_ids = getFriends(screen_name, limit=friends_limit)
        logging.info("Retrieved %d friends ids", len(friend_ids))
        
        follower_ids = getFollowers(screen_name, limit=followers_limit)
        logging.info("Retrieved %d follower ids", len(follower_ids))

        friends_info = getUserInfo(t, r, user_ids=friend_ids, 
                                   sample=friends_sample)
        logging.info("Retrieved user info for %d friends", len(friends_info) )

        logging.info("Getting follower info")
        followers_info = getUserInfo(t, r, user_ids=follower_ids,
                                     sample=followers_sample)
        logging.info("Retrieved user info for %d followers", len(followers_info) )

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
        print "Please supply a screen name."
    else:
        logging.info("Crawling for: %s", SCREEN_NAMES_LIST)
        crawl(SCREEN_NAMES_LIST)
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
