
import os
import urllib
from BeautifulSoup import BeautifulSoup

APP_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join( APP_DIR, 'cache' )


def get_cache():

    bash_cache = set()

    bash_cache_file = os.path.join( CACHE_DIR, 'bash' )
    if (os.path.exists( bash_cache_file )):
        with open( bash_cache_file, 'r' ) as f:
            bash_cache = set ( [ int(i) for i in  set( f.read().split(',') ) ] )

    return bash_cache

def save_cache( bash_cache ):

    if (len(bash_cache) == 0):
        return

    bash_cache_file = os.path.join( CACHE_DIR, 'bash' )
    with open( bash_cache_file, 'w' ) as f:
        bash_cache = [ str(i) for i in bash_cache ]
        f.write( ','.join( bash_cache) )

def get_randoms( bash_cache = None):

    bash_url = "http://bash.org/?random"

    soup = BeautifulSoup( urllib.urlopen(bash_url).read() )

    r = []
    qs = soup.findAll( 'p', attrs = { 'class' : 'quote' }  )
    for q in qs:
        qi = q.text[1:]
        qi = int(qi[:qi.find('+')])
        if ((bash_cache is None) or (qi not in bash_cache)):
            r.append( (qi, str(q.nextSibling) ))
    return r

