# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup

def URLLister(html_in):
    '''
    Input: a string containing html
    Returns a list of the urls found in the html string.
    '''
    return [link.get('href') 
            for link 
            in BeautifulSoup(html_in).find_all('a')]

if __name__ == '__main__':
    
    html_doc = """
    <html><head><title>The Dormouse's story</title></head>
    <body>
    <p class="title"><b>The Dormouse's story</b></p>
    
    <p class="story">Once upon a time there were three little sisters; and their names were
    <a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
    <a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
    <a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
    and they lived at the bottom of a well.</p>
    
    <p class="story">...</p>
    </body>
    </html>
    """
    
    for url in URLLister(html_doc):
        print url