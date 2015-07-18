
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


def browser_open( url = None ):

    def close2():
        try:
            browser.close()
        except:
            log.warning("No browser to close() : %s" % str(url))
    def quit2():
        try:
            browser.quit()
        except:
            log.warning("No browser to quit() : %s" %str(url))

    def close_other_windows():
        o_wind = browser.current_window_handle
        for hnd in browser.window_handles:
            if (hnd == o_wind):
                continue
            browser.switch_to_window(hnd)
            browser.close2()
        browser.switch_to_window(o_wind)

    try:
        profile = webdriver.FirefoxProfile()
        profile.set_preference("webdriver.log.file", os.path.join(LOG_DIR, "firefox.log"))
        browser = webdriver.Firefox(profile)
        #cookies_file = os.path.join( CACHE_DIR, 'cookies' )
        #def __browser_close():
        #    pickle.dump( browser.get_cookies() , open(cookies_file, "wb") )
        #    browser.quit()

        browser.close2 = close2
        browser.quit2 = quit2
        browser.close_other_windows = close_other_windows

        # this is some pythonic voodoo we'll use later
        #browser.close = __browser_close
        browser.maximize_window()
        browser.set_page_load_timeout(90)
        if (url):
            browser.get(url)
        #if (os.path.isfile( cookies_file )):
        #    cookies = pickle.load(open(cookies_file, "rb"))
        #    for cookie in cookies:
        #        browser.add_cookie(cookie)

        # maybe later load cookies here
    except:
        return

    return browser
