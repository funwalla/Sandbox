import redis

r = redis.Redis()

def set_dict_to_redis_hash(dictionary, name, verbose=False):
    
    count = 0
    amount = len(dictionary)
    for item in dictionary:
        r.hset(name, item, dictionary[item])
        count += 1
        if verbose == True and count % 100 == 0:
            print name, count, 'of', amount, 'saved'
            
def get_dict_from_redis(name, verbose=False):
    
    dictionary = r.hgetall(name)
    count = 0
    amount = len(dictionary.keys())
    for item in dictionary:
        dictionary[item] = eval(dictionary[item])
        count += 1
        if verbose == True and count % 100 == 0:
            print name, count, 'of', amount, 'retrieved'
    return dictionary

if __name__ == '__main__':
    
    test_dict = {}
    for i in range(400):
        test_dict[str(i)] = i
        
    print "Saving test dictionary to redis hash:"
    set_dict_to_redis_hash(test_dict, 'test_dict', True)
    
    print "\nGetting test dictionary from redis hash:"
    test_dict_2 = get_dict_from_redis('test_dict', True)
    
    if test_dict.keys().sort() == test_dict_2.keys().sort() and\
       test_dict.values().sort() == test_dict_2.values().sort():
        print "\nTest dictionary successfully retrieved."
    else:
        print "\nERROR: test dictionary not successfully retrieved."
