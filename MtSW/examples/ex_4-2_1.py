# -*- coding: utf-8 -*-

""" Example 4.2 refactored to use my twitter__login module"""

import sys
import time
import cPickle
import twitter
from twitter__login import login


SCREEN_NAME = sys.argv[1]
friends_limit = 10000

t = login()

ids = []
wait_period = 2 #seconds
cursor = -1

while cursor != 0:
    if wait_period > 3600:
        print 'Too many retries. Saving partial data to disk and exiting'
        f = file('%s.friend_ids' % str(cursor), 'wb')
        cPickle.dump(ids, f)
        f.close()
        exit()
                                                
    try:
        response = t.friends.ids(screen_name=SCREEN_NAME,
                                 cursor=cursor)
        ids.extend(response['ids'])
        wait_period = 2
    except twitter.api.TwitterHTTPError, e:
        if e.e.code == 401:
            print 'Encountered 401 Error (Not Authorized)'
            print 'User %s is protecting their tweets' % (SCREEN_NAME, )
        elif e.e.code in (502, 503):
            print 'Encountered %i Error. Trying again in %i seconds' % (e.e.code, wait_period)
            time.sleep(wait_period)
            wait_period *= 1.5
            continue
        elif t.account.rate_limit_status()['remaining_hits'] == 0:
            status = t.account.rate_limit_status()
            now = time.time()  # UTC
            when_rate_limit_resets = status['reset_time_in_seconds'] # UTC
            sleep_time = when_rate_limit_resets - now
            print 'Rate limit reached. Trying again in %i seconds' % (sleep_time, )
            time.sleep(sleep_time)
            continue
    
    cursor = response['next_cursor']
    print >> sys.stderr, 'Fetched %i ids for %s' % (len(ids), SCREEN_NAME)
    if len(ids) >= friends_limit:
        break
    
print ids
