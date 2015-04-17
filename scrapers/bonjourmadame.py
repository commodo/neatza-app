
import sys
sys.path.append('..')

import urllib
from bs4 import BeautifulSoup
import logging as log

def requires_moderation():
    return False

def get_url( from_url = "http://www.bonjourmadame.fr/" ):

    soup = BeautifulSoup( urllib.urlopen(from_url).read() )

    photo_panel_elem = soup.find( 'div', attrs = { 'class' : 'photo post' } )
    cache_key_url = None
    img_url = None
    timestamp_elem = soup.find( 'div', attrs = { 'class' : 'timestamp' } )
    if (timestamp_elem):
        timestamp_a_elem = timestamp_elem.find('a')
        if (timestamp_a_elem):
            cache_key_url = timestamp_a_elem['href']
    if ( photo_panel_elem ):
        img_elem = photo_panel_elem.find( 'img' )
        if ( img_elem ):
            img_url = img_elem['src']

    return (cache_key_url, img_url)

def update_urls( cache_to_compare, cache_to_update, from_page = 1, to_page = None):
    from_url = "http://www.bonjourmadame.fr/page/%d"

    curr_page = from_page
    if (to_page is None):
        to_page = 999999999

    cache_url, img_url = get_url( from_url % curr_page  )
    keep_going = (cache_url is not None) and (img_url is not None)
    while ( keep_going and curr_page <= to_page ):
        log.info( str( ( cache_url, img_url ) ) )
        if (cache_url in cache_to_compare):
            log.info( "  URL '%s' found in cache. Stopping..." % cache_url )
            break
        else:
            cache_to_compare.add( cache_url )
            cache_to_update.add( img_url )

        curr_page += 1

        cache_url, img_url = get_url( from_url % curr_page )
        keep_going = (cache_url is not None) and (img_url is not None)

