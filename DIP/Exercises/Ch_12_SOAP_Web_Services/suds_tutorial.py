import logging
import  suds
logging.basicConfig(level=logging.INFO)

logging.getLogger('suds.client').setLevel(logging.DEBUG)
#logging.getLogger('suds.transport').setLevel(logging.DEBUG)
#logging.getLogger('suds.xsd.scheme').setLevel(logging.DEBUG)
#logging.getLogger('suds.wsdl').setLevel(logging.DEBUG)

from  suds.client import  Client
client =  Client('http://jira.atlassian.com/rpc/soap/jirasoapservice-v2?wsdl')
auth =  client.service.login('funwalla', 'AKcBGwD')

filters = client.service.getFavouriteFilters(auth)
print filters

for filter in filters.getFavouriteFiltersReturn:
    print filter['name']
    print filter['id']
    
client.service.logout(auth)

print "breakpoint"
