from bs4 import BeautifulSoup
import urllib2
import glob
import re
import os.path

image_dir = '/home/john/websites/JESA/images/'
file_dir = '/home/john/websites/JESA/www.yourdon.com/strucanalysis/wiki/index.php/'
fig_files = []
for name in glob.glob(file_dir + 'File_Figure*html'):
    fig_files.append(name)

regex = re.compile('(^http://www.yourdon.com/strucanalysis/wiki/images/[^archive][^thumb].*Figure.*jpg$)')
fig_links = []

for f_file in fig_files:
    f = open(f_file, 'rb')
    soup = BeautifulSoup(f.read())
    
    for link in soup.find_all('a'):
        href = link.get('href')
        if isinstance(href, str) and regex.search(href):
            print href
            fig_links.append(href)
            break

for link in fig_links:
    open_url = urllib2.build_opener()
    page = open_url.open(link)
    figure = page.read()
    file_name = os.path.split(link)[1]
    print 'Writing', file_name
    figure_file = open(image_dir + file_name, 'wb')
    figure_file.write(figure)
    figure_file.close()

#print 'breakpoint'

#regex = re.compile('(http://www.yourdon.com/strucanalysis/wiki/images/[^archive][^thumb].*Figure.*jpg)')
#f_c = []
#for f in figs:
#m = regex.search(f)
#if m: f_c.append(m.group(1))