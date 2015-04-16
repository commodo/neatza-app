
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

    cache = set()
    cache_file = os.path.join( CACHE_DIR, sanitize_url(url) )
    if (os.path.isfile ( cache_file ) ):
        with open( cache_file, 'rb' ) as f:
            cache = set( [ l.strip() for l in  f.read().split(sep) ] )

    return cache

def cache_save( url, cache, sep = '\n' ):

    if (len(cache) == 0):
        return

    ensure_dir( CACHE_DIR )
    cache_file = os.path.join( CACHE_DIR, sanitize_url(url) )
    if (cache and len(cache) > 0):
        with open( cache_file, 'wb' ) as f:
            f.write( sep.join(cache) )
