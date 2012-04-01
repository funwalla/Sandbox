# -*- coding: utf-8 -*-

import twitter
import json

SCREEN_NAME = 'timoreilly'

t = twitter.Twitter(domain='api.twitter.com', api_version='1')
response = t.users.show(screen_name=SCREEN_NAME)
print json.dumps(response, sort_keys=True, indent=4)
