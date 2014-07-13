

import os
import sys
import ConfigParser

APP_DIR = os.path.dirname(os.path.abspath(__file__))
CNF_DIR = os.path.join( APP_DIR, 'conf' )
CACHE_DIR = os.path.join( APP_DIR, 'cache' )
SCRAPERS_DIR = os.path.join( APP_DIR, 'scrapers' )

config = ConfigParser.RawConfigParser(allow_no_value=True)
config.readfp( open( os.path.join( APP_DIR, 'app.settings' ) ) )

scrapers = []
files_in_scrapers_dir = os.listdir(SCRAPERS_DIR)

for fname in files_in_scrapers_dir:

    full_fname = os.path.join( CNF_DIR, fname )
    if (fname[:2] != '__' and fname.endswith('.py')):
        scrapers.append( fname[:-len('.py')] )

sources = {}

for s in scrapers:
    try:
        tags = config.get( 'sources', s )
        tags = tags.split(',')
        tags = [ tag.strip() for tag in tags ]
        sources[s] = tags
    except:
        pass
    
for key, files in sources.items():

    urls_cache = set()
    fname = os.path.join( CACHE_DIR, key )
    if ( os.path.exists( fname ) ):
        with open( fname, 'rb' ) as f:
            urls_cache = set( f.readlines() )
        urls_cache = set([ url_cache.strip() for url_cache in urls_cache ])

    print ("Processing '%s'" % key)
    print ("  Loaded %d URLs from cache" % len(urls_cache))

    print ("  Loading URLs from %s..." % ( key ) ),
    sys.stdout.flush()
    module = __import__('scrapers.' + key, fromlist = ['*'])

    urls = module.get_urls( urls_cache = urls_cache )
    print "got %d urls" % len( urls )
    sys.stdout.flush()

    idx = 0
    for cache_url, img_url in urls:
        if (cache_url in urls_cache):
            print "  URL '%s' is found in the cache. Stopping." % cache_url
            break
        else:
            fname = files[ idx % len( files ) ]
            fname = os.path.join( CNF_DIR, fname + '.conf' )
            with open( fname, 'ab' ) as f:
                f.write( img_url.strip() + '\n' )
            urls_cache.add ( cache_url.strip() )
            idx += 1

    print "  Writing %d URLs to cache" % len( urls_cache )
    sys.stdout.flush()
    fname = os.path.join( CACHE_DIR, key )
    with open( fname, 'wb' ) as f:
        f.write( '\n'.join( [ url_cache.strip() for url_cache in urls_cache ] ) )

