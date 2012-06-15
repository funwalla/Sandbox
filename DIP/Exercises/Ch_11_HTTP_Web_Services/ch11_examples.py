import urllib2,  openanything

# Test script for Sections 11.3, 4, 5, 6

# Changing the User Agent
request = urllib2.Request('http://python.org')
request.add_header('User-Agent', 'DIP/11 funwalla@yahoo.com')
request.add_header('Accept-encoding', 'gzip')

# Another way to add (multiple) headers:
# from: http://pythonfilter.com/blog/changing-or-spoofing-your-user-agent-python.html
#req_headers =  {'User-Agent': ,'open_anything/1.0 funwalla@yahoo.com'}
#request = urllib2.Request('http://python.org',  headers=req_headers)

# Debugging in urllib2
# from: http://mail.python.org/pipermail/tutor/2005-November/043069.html
h = urllib2.HTTPHandler(debuglevel=1)
opener = urllib2.build_opener(h,
                              openanything.DefaultErrorHandler())

print "First data stream:"
#feeddata =  opener.open(request).read()
firstdatastream = opener.open(request)
firstdatastream.headers.dict

#print "\nSecond data stream:"
#request.add_header('If-None-Match',
                   #firstdatastream.headers.get('ETag'))
#seconddatastream =  opener.open(request)
#print 'status:', seconddatastream.status
#seconddatastream.read()


print "breakpoint"

