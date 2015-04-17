#!/usr/bin/env python 

# -*- coding: utf-8 -*-

import sys

import os
import requests

import logging as log

import traceback

import ConfigParser
from utils import cache_load, cache_save, app_prep

log.getLogger("requests").setLevel(log.WARNING)

APP_DIR = os.path.dirname(os.path.abspath(__file__))

_g_dry_run = False

def _update_sources( sources ):

    for key, slist in sources.items():
        for s in slist:
            cache_scraped = cache_load( s )
            cache_send    = cache_load( key + '.send' )
            cache_moderate = cache_load( key + '.moderate' )
            module = __import__('scrapers.' + s, fromlist = [ 'get_urls', 'requires_moderation' ])
            urls = module.get_urls( cache = cache_scraped )
            for cache_url, img_url in urls:
                cache_scraped.add( cache_url )
                if (module.requires_moderation()):
                    cache_moderate.add( img_url )
                else:
                    cache_send.add( img_url )
            if (not _g_dry_run):
                cache_save( cache_scraped )
                cache_save( cache_send )
                cache_save( cache_moderate )

def _build_group_map(config, section):
    map_ = {}

    for i in range(1,9999):
        try:
            id_ = 'group%d' % i
            map_[id_] = [ n.strip() for n in config.get ( section, id_ ).split(',') ]
        except:
            break

    return map_

def main():

    # Read config file
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.readfp( open( os.path.join( APP_DIR, 'app.settings' ) ) )

    # Build reverse maps for names to group names
    sources = _build_group_map( config, 'sources' )

    _update_sources( sources )

if __name__ == "__main__":
    _g_dry_run = 'dry-run' in sys.argv[1:]
    app_prep( 'update_sources.log' )
    try:
        main()
    except Exception as e:
        for line in traceback.format_exc().splitlines():
            log.error( line )

