#!/usr/bin/env python 

# -*- coding: utf-8 -*-

from utils import cache_object, app_prep, load_image_from_url
import traceback
import imagehash

import logging as log

def main():

    log.info( "Caching all images in memory " )
    c1 = cache_object( 'group2.moderate' )

    #hashfunc = imagehash.average_hash
    hashfunc = imagehash.phash
    #hashfunc = imagehash.dhash

    images = {}
    for url in c1:
        img = load_image_from_url(url)
        if (img):
            hash = hashfunc( img )
            images[hash] = images.get(hash, []) + [url]
        else:
            log.warning( url + " not loaded" )
    
    log.info( "Caching done" )

    for k, img_list in images.iteritems():
        if len(img_list) > 1:
            saved_one = False
            log.info("--------------Duplicates------------------")
            for img in img_list:
                if (saved_one):
                    c1.remove(img)
                log.info(img)
                saved_one = True

    c1.save()

if __name__ == "__main__":
    app_prep( 'remove_dups.log' )
    try:
        main()
    except Exception as e:
        for line in traceback.format_exc().splitlines():
            log.error( line )

