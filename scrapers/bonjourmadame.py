
import urllib
from BeautifulSoup import BeautifulSoup
try:
    import concurrent.futures
    HAVE_FUTURES = True
except ImportError:
    HAVE_FUTURES = False

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

    # No rating for this
    return (cache_key_url, img_url, None)

def get_urls( from_page = 1, to_page = None, parallel = True, urls_cache = None):
    from_url = "http://www.bonjourmadame.fr/page/%d"

    curr_page = from_page
    if (to_page is None):
        to_page = 999999999

    urls = []
    if (HAVE_FUTURES and parallel):
        keep_going = True
        MAX_PER_RUN = 10
        MAX_WORKERS = 10
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            while ( keep_going and ((to_page is None) or (curr_page <= to_page)) ):
                futures = []
                for _ in range( min ( MAX_PER_RUN, to_page - curr_page + 1 ) ):
                    futures.append( executor.submit(get_url, ( from_url % curr_page ) ) )
                    curr_page += 1
                for future in concurrent.futures.as_completed(futures):
                    try:
                        result = future.result()
                        print result
                        if (keep_going):
                            keep_going = (result[0] is not None) and (result[1] is not None)
                            cache_url, _ = result
                            if (urls_cache and (cache_url in urls_cache)):
                                print "  URL '%s' found in cache. Stopping..." % cache_url
                                keep_going = False
                            else:
                                urls.append( result )
                    except:
                        keep_going = False
    else:
        result = get_url( from_url % curr_page  )
        keep_going = (result[0] is not None) and (result[1] is not None)
        while ( keep_going and ((to_page is None) or (curr_page <= to_page)) ):
            print result
            cache_url, _ = result
            if (urls_cache and (cache_url in urls_cache)):
                print "  URL '%s' found in cache. Stopping..." % cache_url
                break
            else:
                urls.append( result )
            curr_page += 1
            result = get_url( from_url % curr_page )
            keep_going = (result[0] is not None) and (result[1] is not None)

    return (urls)

