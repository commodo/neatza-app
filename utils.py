
import os
import sys
import random
import logging as log
import Image
import requests
from StringIO import StringIO

APP_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join( APP_DIR, 'cache' )
LOG_DIR = os.path.join( APP_DIR, 'log' )

def load_image_from_url(url):

    if ((url is None) or (len(url) == 0)):
        return None
    try:
        r = requests.get(url)
        f = StringIO(r.content)
        return Image.open(f)
    except:
        return None

def ensure_dir( dirname ):
    if (not os.path.isdir( dirname )):
        os.makedirs( dirname )

def app_prep(log_file):

    reload(sys)
    sys.setdefaultencoding("utf-8")

    nolog = 'nolog' in sys.argv[1:]
    if (nolog):
        log.basicConfig(level = log.INFO)
        log.getLogger("requests").setLevel(log.WARNING)
        return
    ensure_dir(LOG_DIR)
    log.basicConfig(filename = None if nolog else os.path.join( LOG_DIR, log_file ),
                    format   = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level    = log.INFO)
    log.getLogger("requests").setLevel(log.WARNING)

def sanitize_file( _file ):
    return _file.replace('http://', '').replace('https://', '').replace('/', '_')

class cache_object(set):

    def __init__(self, _file, sep = '\n' ):
        set.__init__( self )
        self._file = os.path.join( CACHE_DIR, sanitize_file(_file) )
        self._sep = sep
        self._dry_run = 'dry-run' in sys.argv[1:]

        if (os.path.isfile(self._file)):
            with open( self._file, 'rb' ) as f:
                self.update( set( [ l.strip() for l in f.read().split(sep) ] ) )

    def pop_random(self):
        if (len(self) == 0):
            return
        l = list ( self )
        random.shuffle( l )
        el = l.pop()
        try:
            self.remove( el )
        except:
            pass
        return el

    def save(self):
        if (self._dry_run):
            return
        if (len(self) == 0):
            return

        sanitized = set()
        try:
            sanitized = set( [ str(l) for l in self if l ] )
        except:
            return

        ensure_dir( CACHE_DIR )
        with open( self._file, 'wb' ) as f:
            f.write( self._sep.join(sanitized) )

