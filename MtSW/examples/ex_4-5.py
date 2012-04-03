# -*- coding: utf-8 -*-

import sys
import json
import redis
from twitter__login import login

# A makeTwitterRequest call through to the /users/lookup 
# resource, which accepts a comma separated list of up 
# to 100 screen names. Details are fairly uninteresting. 
# See also http://dev.twitter.com/doc/get/users/lookup
#
# JW: adapted original code to retrieve user_ids from redis
# and pass them to the getUserInfo function.
#
from twitter__util import getUserInfo

t = login()
r = redis.Redis()

friend_ids = list( r.smembers("screen_name$timoreilly$friend_ids") )

user_info = getUserInfo(t, r, user_ids = friend_ids)

print json.dumps( user_info, indent=4)
