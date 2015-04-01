
import os
import urllib
from BeautifulSoup import BeautifulSoup
from utils import cache_load, cache_save

def get_cache():
    return  set( cache_load( 'bash', sep = ',' ) )

def save_cache( bash_cache ):
    cache_save( 'bash', bash_cache, sep = ',' )

def get_randoms( bash_cache = None):

    bash_url = "http://bash.org/?random"

    soup = BeautifulSoup( urllib.urlopen(bash_url).read() )

    r = []
    qs = soup.findAll( 'p', attrs = { 'class' : 'quote' }  )
    for q in qs:
        qi = q.text[1:]
        qi = str(int(qi[:qi.find('+')]))
        if ((bash_cache is None) or (qi not in bash_cache)):
            r.append( (qi, str(q.nextSibling) ))
    return r

