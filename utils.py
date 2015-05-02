
import os
import sys
import logging as log
import Image
import requests
import cStringIO

APP_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join( APP_DIR, 'cache' )
LOG_DIR = os.path.join( APP_DIR, 'log' )

def load_image_from_url(img_url):

    if (img_url is None or len(img_url) == 0):
        return None
    try:
        r = requests.get(img_url)
        f = cStringIO.StringIO(r.raw.read())
        return Image.open(f)
    except:
        return None

def dhash(image, hash_size = 8):

    # Grayscale and shrink the image in one step.
    image = image.convert('L').resize(
        (hash_size + 1, hash_size),
        Image.ANTIALIAS,
    )

    pixels = list(image.getdata())

    # Compare adjacent pixels.
    difference = []
    for row in xrange(hash_size):
        for col in xrange(hash_size):
            pixel_left = image.getpixel((col, row))
            pixel_right = image.getpixel((col + 1, row))
            difference.append(pixel_left > pixel_right)

    # Convert the binary array to a hexadecimal string.
    decimal_value = 0
    hex_string = []
    for index, value in enumerate(difference):
        if value:
            decimal_value += 2**(index % 8)
        if (index % 8) == 7:
            hex_string.append(hex(decimal_value)[2:].rjust(2, '0'))
            decimal_value = 0

    return ''.join(hex_string)

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

    def __init__(self, _file, sep = '\n' ):
        set.__init__( self )
        self._file = os.path.join( CACHE_DIR, sanitize_file(_file) )
        self._dump_counter = 50
        self._sep = sep
        self._dry_run = 'dry-run' in sys.argv[1:]

        if (os.path.isfile(self._file)):
            with open( self._file, 'rb' ) as f:
                self.update( set( [ l.strip() for l in f.read().split(sep) ] ) )

    def add(self, elem):
        if (elem is None or not isinstance(elem, str)):
            return

        set.add(self, elem)
        if (self._dry_run):
            return

        self._dump_counter -= 1

        if (self._dump_counter <= 0):
            self._dump_counter = 50
            self.save()

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

