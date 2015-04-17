
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

def sanitize_file( _file ):
    return _file.replace('http://', '').replace('https://', '').replace('/', '_')

class cache_object(set):

    def __init__(self, _file, sep = '\n', dry_run = False ):
        set.__init__( self)
        self._file = os.path.join( CACHE_DIR, sanitize_file(_file) )
        self._dump_counter = 50
        self._sep = sep
        self._dry_run = dry_run

        if (os.path.isfile(self._file)):
            with open( self._file, 'rb' ) as f:
                self.update( set( [ l.strip() for l in  f.read().split(sep) ] ) )

    def add(self, *args, **kw_args):
        set.add(self, *args, **kw_args)
        if (self._dry_run):
            return

        self._dump_counter -= 1

        if (self._dump_counter <= 0):
            self._dump_counter = 50
            self.save()

    def save(self):
        if (self._dry_run):
            return

        ensure_dir( CACHE_DIR )
        with open( self._file, 'wb' ) as f:
            f.write( self._sep.join(self) )

