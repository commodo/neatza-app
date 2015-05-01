
import sys
sys.path.append('..')

import wordpress as w
import logging as log

def requires_moderation():
    return True

def update_urls( cache_to_compare, cache_to_update, from_page = 1, to_page = None ):
    base_url = "http://thebrigade.com/category/funny/bad-idea-weekend/page/%d"

    return w.update_urls( base_url, cache_to_compare, cache_to_update, from_page, to_page )

