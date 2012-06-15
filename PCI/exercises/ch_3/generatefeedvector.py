import feedparser
import re
import redis

def getwords(html):
  # Remove all the HTML tags
  txt=re.compile(r'<[^>]+>').sub('',html)

  # Split words by all non-alpha characters
  words=re.compile(r'[^A-Z^a-z]+').split(txt)

  # Convert to lowercase
  return [word.lower() for word in words if word!='']

# Returns title and dictionary of word counts for an RSS feed
def getwordcounts(url):
  
  # Parse the feed
  d = feedparser.parse(url)
  wc = {}

  # Loop over all the entries
  for e in d.entries:
    if 'summary' in e: summary = e.summary
    else: summary = e.description

    # Extract a list of words
    words = getwords(e.title + ' ' + summary)
    for word in words:
      wc.setdefault(word,0)
      wc[word] += 1
      
  return d.feed.title,wc

  
if __name__ == '__main__':
  
  ##get a sample rss_feed
  #rss_feed = 'http://news.google.com/news?ned=uk&topic=n&output=rss'
  #word_count = getwordcounts(rss_feed)
  
  apcount={}
  wordcounts={}
  feedlist=[line for line in file('feedlist.txt')]
  for feedurl in feedlist:
    print "Current url: " + feedurl
    try:
      title,wc=getwordcounts(feedurl)
      wordcounts[title]=wc
      for word,count in wc.items():
        apcount.setdefault(word,0)
        if count>1:
          apcount[word]+=1
    except:
      print 'Failed to parse feed %s' % feedurl
      

  r = redis.Redis()
  
  ## Save to redis
  #for item in wordcounts:
    #r.hset('wordcounts', item, wordcounts[item])
  #for item in apcount:
    #r.hset('apcount', item, apcount[item])
    
  # Retrieve from redis
  wordcounts = r.hgetall('wordcounts')
  count = 0
  amount = len(wordcounts)
  for item in wordcounts:
    wordcounts[item] = eval(wordcounts[item])
    count += 1
    print "wordcounts:", count, 'of', amount
    
  apcount = r.hgetall('apcount')
  count = 0
  amount = len(apcount)
  for item in apcount:
    apcount[item] = eval(apcount[item])
    count += 1
    print "apcount:", count, 'of', amount
    
  
  wordlist=[]
  for w,bc in apcount.items():
    frac=float(bc)/len(wordcounts)
    if frac>0.1 and frac<0.5:
      wordlist.append(w)
  
  out=file('blogdata1.txt','w')
  out.write('Blog')
  for word in wordlist: out.write('\t%s' % word)
  out.write('\n')
  for blog,wc in wordcounts.items():
    print blog
    out.write(blog)
    for word in wordlist:
      if word in wc: out.write('\t%d' % wc[word])
      else: out.write('\t0')
    out.write('\n')  
  
  print "breakpoint"