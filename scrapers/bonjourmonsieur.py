
import urllib
from urlparse import urljoin
from BeautifulSoup import BeautifulSoup

def get_url( from_url = "http://www.bonjourmonsieur.fr/", base_url = "http://www.bonjourmonsieur.fr/" ):

    soup = BeautifulSoup( urllib.urlopen(from_url).read() )

    photo_panel_elem = soup.find( 'div', attrs = { 'class' : 'boxgrid captionfull' } )
    img_url = None
    if ( photo_panel_elem ):
        img_elem = photo_panel_elem.find( 'img' )
        if ( img_elem ):
            img_url = urljoin( base_url, img_elem['src'])

    next_url = None
    next_link_elem = soup.find( 'div', attrs = { 'style' : 'float:left' })
    if (next_link_elem):
        link_elem = next_link_elem.find( 'a' )
        if (link_elem):
            next_url = urljoin( base_url, link_elem['href'])

    rating = None
    rating_elem = soup.find( 'div', attrs = { 'class' : 'average_rating' } )
    if (rating_elem):
        rating_str = rating_elem.text
        if (rating_str):
            rating_str_elems = rating_str.split('/')
            if (rating_str_elems):
                rating = float(rating_str_elems[0].strip())

    return (img_url, next_url, rating)

def get_urls( min_rating = 7.00, parallel = False, urls_cache = None ):
    from_url = "http://www.bonjourmonsieur.fr/"

    idx = 1
    urls = []
    img_url, next_url, rating = get_url( from_url )
    while ( next_url ):
        print idx, '---', next_url, img_url
        if (urls_cache and (next_url in urls_cache)):
            print "  URL '%s' found in cache. Stopping..." % next_url
            break
        if (min_rating <= rating):
            urls.append( (from_url, img_url) )
        from_url = next_url
        img_url, next_url, rating = get_url( next_url )
        idx += 1

    return (urls)

