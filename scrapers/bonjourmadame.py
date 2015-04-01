
import urllib
from BeautifulSoup import BeautifulSoup
import logging as log

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

def get_urls( from_page = 1, to_page = None, cache = None):
    from_url = "http://www.bonjourmadame.fr/page/%d"

    curr_page = from_page
    if (to_page is None):
        to_page = 999999999

    urls = []
    result = get_url( from_url % curr_page  )
    keep_going = (result[0] is not None) and (result[1] is not None)
    while ( keep_going and ((to_page is None) or (curr_page <= to_page)) ):
        log.info( str( result ) )
        cache_url, _ = result
        if (cache and (cache_url in cache)):
            log.info( "  URL '%s' found in cache. Stopping..." % cache_url )
            break
        else:
            urls.append( result )
        curr_page += 1
        result = get_url( from_url % curr_page )
        keep_going = (result[0] is not None) and (result[1] is not None)

    return (urls)

