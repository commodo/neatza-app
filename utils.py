
import os
import sys
import logging as log

APP_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join( APP_DIR, 'cache' )
LOG_DIR = os.path.join( APP_DIR, 'log' )

def ensure_dir( dirname ):
    if (not os.path.isdir( dirname )):
        os.makedirs( dirname )

def app_prep(log_file):

    nolog = 'nolog' in sys.argv[1:]
    if (nolog):
        log.getLogger().setLevel(log.INFO)
        return
    ensure_dir(LOG_DIR)
    log.basicConfig(filename = None if nolog else os.path.join( LOG_DIR, log_file ),
                    format   = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level    = log.INFO)

def sanitize_url( url ):
    return url.replace('http://', '').replace('https://', '').replace('/', '_')

def cache_load( url, sep = '\n'):

    class cache_object(set):
        def __init__(self, *args, **kw_args):
            set.__init__( self, *args, **kw_args )
            self._file = None

    cache = cache_object()
    cache_file = os.path.join( CACHE_DIR, sanitize_url(url) )
    if (os.path.isfile ( cache_file ) ):
        with open( cache_file, 'rb' ) as f:
            cache = cache_object( [ l.strip() for l in  f.read().split(sep) ] )
    cache._file = cache_file

    return cache

def cache_save( cache, sep = '\n' ):

    if (cache._file is None):
        return

    if (len(cache) == 0):
        return

    ensure_dir( CACHE_DIR )
    with open( cache._file, 'wb' ) as f:
        f.write( sep.join(cache) )
