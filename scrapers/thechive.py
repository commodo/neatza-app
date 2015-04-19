
import sys
sys.path.append('..')

import urllib
from bs4 import BeautifulSoup
import logging as log

def requires_moderation():
    return True

def get_blog_entry_urls( blog_entry_url ):

    soup = BeautifulSoup( urllib.urlopen(blog_entry_url).read() )
    imgs = soup.findAll( 'img', attrs = { 'class' : 'attachment-full' } )

    return [ img['src'] for img in imgs ]


def update_urls( cache_to_compare, cache_to_update, from_page = 1, to_page = None ):
    base_url = "http://thechive.com/category/girls/page/%d"

    curr_page = from_page
    if (to_page is None):
        to_page = 999999999

    urls = []
    keep_going = True
    while (keep_going):
        soup = BeautifulSoup( urllib.urlopen(base_url % curr_page).read() )
        blog_urls = soup.findAll( 'h2', attrs = { 'itemprop' : 'headline' } )
        if (len(blog_urls) == 0):
            break
        blog_urls = [ u.find( 'a' )['href'] for u in blog_urls ]

        for blog_url in blog_urls:
            if (cache_to_compare and (blog_url in cache_to_compare)):
                keep_going = False
                log.info( "  URL '%s' found in cache. Stopping..." % blog_url )
                break
            for img_url in get_blog_entry_urls(blog_url):
                log.info( str((blog_url, img_url)) )
                cache_to_compare.add( blog_url )
                cache_to_update.add( img_url )

        curr_page += 1
        if (curr_page == to_page):
            break

