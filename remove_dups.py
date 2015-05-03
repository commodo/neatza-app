#!/usr/bin/env python 

# -*- coding: utf-8 -*-

from utils import cache_object, app_prep, load_image_from_url, dhash
import traceback

import logging as log

def main():

    log.info( "Caching all images in memory " )
    c1 = cache_object( 'group2.moderate' )
    images = [ (el, load_image_from_url(el) ) for el in c1 ]
    images = [ (el, dhash(img)) for el, img in images if img ]
    log.info( "Caching done" )
    for f1, h1 in images:
        for f2, h2 in images:
            if (h1 == h2):
                print str((f1, f2)), "are similar"


if __name__ == "__main__":
    app_prep( 'remove_dups.log' )
    try:
        main()
    except Exception as e:
        for line in traceback.format_exc().splitlines():
            log.error( line )

