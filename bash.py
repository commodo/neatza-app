#!/usr/bin/env python 

# -*- coding: utf-8 -*-

import os
import urllib
from bs4 import BeautifulSoup
from utils import cache_object

def get_randoms( bash_cache = None):

    bash_url = "http://bash.org/?random"

    soup = BeautifulSoup( urllib.urlopen(bash_url).read() )

    r = []
    qs = soup.findAll( 'p', attrs = { 'class' : 'quote' }  )
    for q in qs:
        qi = q.text[1:]
        qi = str(int(qi[:qi.find('+')]))
        if ((bash_cache is None) or (qi not in bash_cache)):
            r.append( (qi, unicode(q.nextSibling).encode('utf-8') ))
    return r

