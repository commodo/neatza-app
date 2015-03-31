#!/usr/bin/env python 

# -*- coding: utf-8 -*-

"""
Neatza App

Or morning app; morning from the 'Good Morning' greeting.

Simple application that sends emails + quotes with pictures to an 
email address, preferably an emailing list.

The email is currently comprised of a Quote of the Day + a picture.
The picture can be of whatever you want it to be.

To make this work, you'll need to add '.conf' files where the neatza_app.py
file is located and just let it run over a cron-job.

"""

import sys
import bash
import email1
from qotds import get_qotds

from time import gmtime, strftime
import os
from PIL import Image
import requests
import cStringIO
import random

import logging as log

import traceback

import ConfigParser

_g_dry_run = False
log.getLogger("requests").setLevel(log.WARNING)

APP_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join( APP_DIR, 'log' )
CACHE_DIR = os.path.join( APP_DIR, 'cache' )

def valid_image(img_url):
    """ Validates that the given URL is actually a valid image.
        Returns True if there's a valid image at the given URL, and False otherwise.

        img_url -- The URL of the possible image.
    """

    if (img_url is None or len(img_url) == 0):
        return False
    try:
        r = requests.get(img_url)
        f = cStringIO.StringIO(r.raw.read())
        Image.open(f)
        return True
    except:
        log.error("URL '%s' is not a valid image" % img_url)
        return False

def extract_an_url(fname):
    """ Extracts from a filename the list

        The file is re-written without the extracted URL.

        fname -- The filename from which to extract the values.
    """
    urls = []

    if (os.path.isfile(fname)):
        with open(fname, 'r') as f:
            urls = [ url.strip() for url in f.readlines() ]
            urls = [ url for url in urls if len(url) > 0 ]

    random.shuffle(urls)

    url = None
    while ((url is None) and (len(urls) > 0)):
        url = urls.pop()
        if (not valid_image(url)):
            url = None

    if (_g_dry_run):
        return url

    # will empty file if len(urls) == 0
    with open(fname, 'w') as f:
        f.write('\n'.join(urls))

    return (url)

def _get_url_for_name( sources, group ):

    if (group not in sources):
        return
    source_group = sources[group]

    src = None
    url = None
    for s in source_group['sources']:
        if (source_group.get( s + '_used' )):
            continue
        module = __import__('scrapers.' + s, fromlist = [ 'get_url' ])
        _, url, _ = module.get_url()
        if (url):
            source_group[ s + '_used' ] = True
            return url

    for s in source_group['sources']:
        url = extract_an_url( os.path.join( CACHE_DIR, s ) )
        if (url):
            return url

def _get_to_addrs(config, tag, default_dst_addr = None):

    to_addrs = []
    try:
        to_addrs = config.get ( 'email_overrides', tag )
        to_addrs = list( set( to_addrs.split(',') ) )
    except:
        to_addrs = []
        if (default_dst_addr):
            to_addrs.append(default_dst_addr)

    return to_addrs

def _get_bash_text( bash_data ):

    bash_fresh, bash_cache = bash_data

    bash_text = ""
    if (len(bash_fresh) > 0):
        bash_id, bash_text = bash_fresh.pop()
        bash_cache.add(bash_id)

    return bash_text

def _send_neatza( server, from_addr, tag, qotds, bash_data, img_url, to_addrs ):

    quote, qauth = "", ""
    if (len(qotds) > 0):
        quote, qauth = qotds.pop()
    bash_text = _get_bash_text( bash_data )

    subject = u'[%s] from neatza app' % strftime("%Y-%m-%d", gmtime())
    msg_text = (u'Random Quote Of The Day for %s\n%s\n%s' % (tag.title(), quote, qauth)) + \
               (u'\n\nRandom Bash.Org\n%s' % bash_text ) + \
               (u'\n\n%s' % img_url )
    msg_html = (u'<div><b>Random Quote Of The Day for %s</b>' % (tag.title()) ) + \
               (u'<div style="margin-left: 30px; margin-top: 10px">') + \
               (u'%s<br/><b>%s</b></div></div>' % (quote, qauth) ) + \
               (u'<br/><br/>') + \
               (u'<div><b>Random Bash.Org</b><br />') + \
               (u'%s</div>' % bash_text) + \
               (u'<br/><br/>') + \
               (u'<img src="%s" style="max-width: 700px" >' % img_url )

    if (_g_dry_run):
        return

    email1.send(server    = server,
                from_addr = from_addr,
                to_addrs  = to_addrs,
                subject   = subject,
                msg_text  = msg_text,
                msg_html  = msg_html)

def _build_group_reverse_map(config, section):
    rev_map = {}
    for i in range(1,9999):
        try:
            id_ = 'group%d' % i
            names = [ n.strip() for n in config.get ( section, id_ ).split(',') ]
            for name in names:
                rev_map[name] = id_
        except:
            break

    return rev_map

def _build_group_map(config, section):
    map_ = {}

    for i in range(1,9999):
        try:
            id_ = 'group%d' % i
            names = [ n.strip() for n in config.get ( section, id_ ).split(',') ]
            map_[id_] = { section : names }
        except:
            break

    return map_

def main():

    qotds = get_qotds()

    # Read config file
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.readfp( open( os.path.join( APP_DIR, 'app.settings' ) ) )

    # Login credentials
    email_addr = config.get( 'mail', 'address' )
    email_pass = config.get( 'mail', 'password' )
    # Default destination email
    default_dst_addr = config.get ( 'mail', 'destination' )

    # Build reverse maps for names to group names
    names_map = _build_group_reverse_map( config, 'names' )
    sources   = _build_group_map( config, 'sources' )

    # Get the names into a list and shuffle them
    names = list(names_map.keys())
    random.shuffle( names )

    # Get a list of random IDs and the ones we've sent (and cached)
    bash_data = (bash.get_randoms(), bash.get_cache())

    server = None if _g_dry_run else email1.get_server(email_addr, email_pass)

    for name in names:

        to_addrs = _get_to_addrs(config, name, default_dst_addr)
        if (len(to_addrs) == 0):
            continue

        url = _get_url_for_name( sources, names_map[name] )

        if (url is None):
            log.warning("No image URL for '%s'", name)

        _send_neatza( server, email_addr, name, qotds, bash_data, url, to_addrs )

    if (not _g_dry_run):
        server.quit()
        bash.save_cache (bash_data[1])

if __name__ == "__main__":
    args = sys.argv[1:]
    nolog = 'nolog' in args
    _g_dry_run = 'dry-run' in args
    if (not nolog):
        log.basicConfig(filename = os.path.join( LOG_DIR, 'neatza_app.log' ),
                        format   = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level    = log.INFO)
    try:
        main()
    except Exception as e:
        for line in traceback.format_exc().splitlines():
            log.error( line )

