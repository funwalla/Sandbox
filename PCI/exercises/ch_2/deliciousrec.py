from pydelicious import get_popular,get_userposts,get_urlposts
import time
import redis
import random
import recommendations

def initializeUserDict(tag,count=5):
  user_dict={}
  # get the top count' popular posts
  for p1 in get_popular(tag=tag)[0:count]:
    # find all users who posted this
    for p2 in get_urlposts(p1['url']):
      user=p2['user']
      user_dict[user]={}
  return user_dict

def fillItems(user_dict):
  all_items={}
  # Find links posted by all users
  
  count = 0
  len_ud = len(user_dict)
  for user in user_dict:
    count += 1
    print "Processing user %d of %d" % (count, len_ud)
    posts = []
    for i in range(3):
      try:
        posts=get_userposts(user)
        break
      except:
        print "Failed user "+user+", retrying"
        time.sleep(4)
    for post in posts:
      url=post['url']
      user_dict[user][url]=1.0
      all_items[url]=1
  
  # Fill in missing items with 0
  for ratings in user_dict.values():
    for item in all_items:
      if item not in ratings:
        ratings[item]=0.0
        
def save_user_dict(user_dict):
  r = redis.Redis()
  count = 0
  len_ud = len(user_dict)
  for k in user_dict:
    r.hset("user_dict", k, user_dict[k])
    print "Saved %d of %d to redis hash 'user_dict'" % (count, len_ud)
    count += 1  

def get_user_dict(user_dict_key):
  """ Retrieve user dictionary from Redis."""
  user_dict = {}
  r = redis.Redis()
  for key in r.hkeys(user_dict_key):
    if key == '':
      continue
    user_dict[key] = eval(r.hget(user_dict_key,key))
  return user_dict


if __name__ == '__main__':
  
  #user_dict = initializeUserDict('programming')
  #fillItems(user_dict)
  #save_user_dict(user_dict)
  
  user_dict = get_user_dict('user_dict')
  
  # Find users most like a given user
  user = user_dict.keys()[random.randint(0, len(user_dict)-1)]
  top_matches = recommendations.topMatches(user_dict, user)
  
  print "Top matches for", user, ":"
  print "{0:6}    {1}".format( "Score", "Name")
  for match in top_matches:
    print "{0:.4f}    {1:6}".format(match[0], match[1])
  
  print "\nRecommended URLs for", user, ":"
  recs = recommendations.getRecommendations(user_dict, user)[0:10]
  
  print "{0:6}    {1}".format( "Score", "URL")
  for item in recs:
      print "{0:.4f}    {1}".format(item[0], item[1])
      
  print "placeholder for breakpoint"