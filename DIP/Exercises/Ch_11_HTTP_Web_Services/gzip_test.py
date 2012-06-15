import gzip
import os
import hashlib

def get_hash(data):
    return hashlib.md5(data).hexdigest()

def percent_reduction(orig, reduced):
    return 100 * round(1.0*reduced/orig, 5)

data = open('lorem.txt', 'r').read() * 1024
cksum = get_hash(data)
orig_size =  len(data)

print 'Level  Size        %       Checksum'
print '-----  ----------  ------  ---------------------------------'
print 'data   %10d  %6.2f   %s' % (orig_size, 100, cksum)

for i in xrange(1, 10):
    filename = 'compress-level-%s.gz' % i
    output = gzip.open(filename, 'wb', compresslevel=i)
    try:
        output.write(data)
    finally:
        output.close()
    size = os.stat(filename).st_size
    pc_orig =  percent_reduction(orig_size, size)
    cksum = get_hash(open(filename, 'rb').read())
    print '%5d  %10d  %6.2f   %s' % (i, size, pc_orig, cksum)