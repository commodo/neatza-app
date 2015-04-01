
import urllib
from urlparse import urljoin
from BeautifulSoup import BeautifulSoup
import logging as log

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

def get_urls( min_rating = 7.00, cache = None ):
    from_url = "http://www.bonjourmonsieur.fr/"

    idx = 1
    urls = []
    img_url, next_url, rating = get_url( from_url )
    while ( next_url ):
        log.info( str(( idx, '---', next_url, img_url )) )
        if (cache and (next_url in cache)):
            log.info( str(( "  URL '%s' found in cache. Stopping..." % next_url )) )
            break
        if (min_rating <= rating):
            urls.append( (from_url, img_url) )
        from_url = next_url
        img_url, next_url, rating = get_url( next_url )
        idx += 1

    return (urls)

