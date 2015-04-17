
import sys
sys.path.append('..')

import urllib
from urlparse import urljoin
from bs4 import BeautifulSoup
import logging as log

def requires_moderation():
    return False

def get_url( from_url = "http://www.bonjourmonsieur.fr/", base_url = "http://www.bonjourmonsieur.fr/" ):

    soup = BeautifulSoup( urllib.urlopen(from_url).read() )

    div_img_elem = soup.find( 'div', attrs = { 'class' : 'img' } )
    img_url = None
    if ( div_img_elem ):
        img_elem = div_img_elem.find( 'img' )
        if ( img_elem ):
            img_url = urljoin( base_url, img_elem['src'])

    next_url = None
    next_link_elem = soup.find( 'a', attrs = { 'id' : 'previous' })
    if (next_link_elem):
        next_url = urljoin( base_url, next_link_elem['href'])

    rating = None
    rating_elem = soup.find( 'div', attrs = { 'class' : 'vote' } )
    if (rating_elem):
        span = rating_elem.find( 'span' )
        if (span):
            rating = float(span.text.split('/')[0])

    return (img_url, next_url, rating)

def update_urls( cache_to_compare, cache_to_update, min_rating = 7.00 ):
    from_url = "http://www.bonjourmonsieur.fr/"

    idx = 1
    img_url, next_url, rating = get_url( from_url )
    while ( next_url ):
        log.info( str(( idx, '---', next_url, img_url )) )
        if (cache_to_compare and (next_url in cache_to_compare)):
            log.info( str(( "  URL '%s' found in cache. Stopping..." % next_url )) )
            break
        if (min_rating <= rating):
            if (cache_to_compare):
                cache_to_compare.add( from_url )
            cache_to_update.add( img_url )
        from_url = next_url
        img_url, next_url, rating = get_url( next_url )
        idx += 1

