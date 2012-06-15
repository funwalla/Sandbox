# A dictionary of movie critics and their ratings of a small
# set of movies
critics={'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
 'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5, 
 'The Night Listener': 3.0},
'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5, 
 'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0, 
 'You, Me and Dupree': 3.5}, 
'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
 'Superman Returns': 3.5, 'The Night Listener': 4.0},
'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
 'The Night Listener': 4.5, 'Superman Returns': 4.0, 
 'You, Me and Dupree': 2.5},
'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0, 
 'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
 'You, Me and Dupree': 2.0}, 
'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
 'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
'Toby': {'Snakes on a Plane':4.5,'You, Me and Dupree':1.0,'Superman Returns':4.0}}

from math import sqrt

# Returns a distance-based similarity score for person1 and person2
def sim_distance(prefs,person1,person2):
  # Get the list of shared_items
  si={}
  for item in prefs[person1]: 
    if item in prefs[person2]: si[item]=1

  # if they have no ratings in common, return 0
  if len(si)==0: return 0

  # Add up the squares of all the differences
  sum_of_squares=sum([ pow(prefs[person1][item] - prefs[person2][item],2) 
                      for item in prefs[person1] if item in prefs[person2]])

  return 1/(1+sum_of_squares)


# Returns the Pearson correlation coefficient for p1 and p2
def sim_pearson(prefs,p1,p2):
  # Get the list of mutually rated items
  si={}
  for item in prefs[p1]: 
    if item in prefs[p2]: si[item]=1

  # if they are no ratings in common, return 0
  if len(si)==0: return 0

  # Sum calculations
  n=len(si)
  
  # Sums of all the preferences
  sum1=sum([prefs[p1][it] for it in si])
  sum2=sum([prefs[p2][it] for it in si])
  
  # Sums of the squares
  sum1Sq=sum([pow(prefs[p1][it],2) for it in si])
  sum2Sq=sum([pow(prefs[p2][it],2) for it in si])	
  
  # Sum of the products
  pSum=sum([prefs[p1][it]*prefs[p2][it] for it in si])
  
  # Calculate r (Pearson score)
  num=pSum-(sum1*sum2/n)
  den=sqrt((sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n))
  if den==0: return 0

  r=num/den

  return r

# Returns the best matches for person from the prefs dictionary. 
# Number of results and similarity function are optional params.
def topMatches(prefs,person,n=5,similarity=sim_pearson):
  
  scores=[(similarity(prefs,person,other),other) 
                  for other in prefs if other!=person]
       
  scores.sort()
  scores.reverse()
  return scores[0:n]

# Gets recommendations for a person by using a weighted average
# of every other user's rankings
def getRecommendations(prefs,person,similarity=sim_pearson):
  totals={}
  simSums={}
  for other in prefs:
    # don't compare me to myself
    if other==person: continue
    sim=similarity(prefs,person,other)

    # ignore scores of zero or lower
    if sim<=0: continue
    for item in prefs[other]:
	    
      # only score movies I haven't seen yet
      if item not in prefs[person] or prefs[person][item]==0:
        # Similarity * Score
        totals.setdefault(item,0)
        totals[item]+=prefs[other][item]*sim
        # Sum of similarities
        simSums.setdefault(item,0)
        simSums[item]+=sim

  # Create the normalized list
  rankings=[(total/simSums[item],item) for item,total in totals.items()]

  # Return the sorted list
  rankings.sort()
  rankings.reverse()
  return rankings

def transformPrefs(prefs):
  result={}
  for person in prefs:
    for item in prefs[person]:
      result.setdefault(item,{})
      # Flip item and person
      result[item][person]=prefs[person][item]
  return result

def calculateSimilarItems(prefs, n=10):
  # Create a dictionary of items showing which other items they
  # are most similar to.

  result = {}
  # Invert the preference matrix to be item-centric
  itemPrefs = transformPrefs(prefs)

  count = 0
  for item in itemPrefs:
    # Status updates for large datasets
    count += 1 
    if count % 100 == 0: print "%d / %d" % (count,len(itemPrefs))
    # Find the most similar items to this one
    scores = topMatches(itemPrefs, item ,n=n, similarity=sim_distance)
    result[item] = scores

  return result

def getRecommendedItems(prefs,itemMatch,user):
  userRatings=prefs[user]
  scores={}
  totalSim={}
  # Loop over items rated by this user
  for (item,rating) in userRatings.items( ):

    # Loop over items similar to this one
    for (similarity,item2) in itemMatch[item]:

      # Ignore if this user has already rated this item
      if item2 in userRatings: continue
      # Weighted sum of rating times similarity
      scores.setdefault(item2,0)
      scores[item2]+=similarity*rating
      # Sum of all the similarities
      totalSim.setdefault(item2,0)
      totalSim[item2]+=similarity

  # Divide each total score by total weighting to get an average
  rankings=[(score/totalSim[item],item) for item,score in scores.items( )]

  # Return the rankings from highest to lowest
  rankings.sort( )
  rankings.reverse( )
  return rankings

def loadMovieLens(path='/home/john/data/Movie_Lens/ml-100k'):
  # Get movie titles
  movies={}
  for line in open(path+'/u.item'):
    (id,title)=line.split('|')[0:2]
    movies[id]=title
  
  # Load data
  prefs={}
  for line in open(path+'/u.data'):
    (user,movieid,rating,ts)=line.split('\t')
    prefs.setdefault(user,{})
    prefs[user][movies[movieid]]=float(rating)
  return prefs


if __name__ == '__main__':
  
  print "sim_distance(critics, 'Lisa Rose', 'Gene Seymour')"
  print sim_distance(critics, 'Lisa Rose', 'Gene Seymour')

  print "\nsim_pearson(critics, 'Lisa Rose', 'Gene Seymour')"
  print sim_pearson(critics, 'Lisa Rose', 'Gene Seymour')

  print "\ntopMatches(critics, 'Toby', n=3)"
  for item in topMatches(critics, 'Toby', n=3):
    print "%s:\t%1.3f" % (item[1], item[0])
  
  print "Find similiar people and recommend products"
  print "\ngetRecommendations(critics, 'Toby') using Pearson"
  print getRecommendations(critics, 'Toby')
  
  print "\ngetRecommendations(critics, 'Toby') using Euclidean"
  print getRecommendations(critics, 'Toby')
  
  print "\nFind similar products"
  movies = transformPrefs(critics)
  print "topMatches(movies, 'Superman Returns')"
  top_matches = topMatches(movies, 'Superman Returns')
  for item in top_matches:
    print item
  
  print "\nFinding similar items"
  item_sim = calculateSimilarItems(critics)
  for item in item_sim:
    print "\n" + item
    for rating in item_sim[item]:
      print "%1.3f  %s" % rating
      
  print "\ngetRecommendedItems(critics, item_sim, 'Toby')"
  item_recs = getRecommendedItems(critics, item_sim, 'Toby')
  for item in item_recs:
    print "%1.3f  %s" % item
  
  print "\ngetting Movie Lens user recommendations for user '87'"
  prefs = loadMovieLens()
  movie_recs = getRecommendations(prefs, '87')[0:10]
  for item in movie_recs:
    print "%1.1f  %s" % item
    
    print "\ngetting Movie Lens item recommendations for user '87'"
    item_sim_ml = calculateSimilarItems(prefs, n=50)
    movie_item_recs = getRecommendedItems(prefs, item_sim_ml,'87')[0:10]
    for item in movie_item_recs:
      print "%1.1f  %s" % item
      
  
  print "\nAll tests completed"  