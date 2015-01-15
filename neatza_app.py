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

import bash
from qotds import get_qotds

import smtplib
from time import gmtime, strftime
import os
from PIL import Image
import urllib, cStringIO
import random

import logging as log

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import traceback

import ConfigParser

APP_DIR = os.path.dirname(os.path.abspath(__file__))
CNF_DIR = os.path.join( APP_DIR, 'conf' )
LOG_DIR = os.path.join( APP_DIR, 'log' )
CACHE_DIR = os.path.join( APP_DIR, 'cache' )

# When email fails https://support.google.com/mail/answer/14257

def sendemail(from_addr, to_addr_list, cc_addr_list, bcc_addr_list,
              subject, msg_text, msg_html,
              login, password,
              smtpserver='smtp.gmail.com:587'):
    """ Sends an email to a set of recipients by using a SMTP sever

        from_addr -- The email address of the sender
        to_addr_list -- A list of destination email addresses
        cc_addr_list -- A list of CC destination email addresses
        bcc_addr_list -- A list of BCC destination email addresses
        subject -- Subject of the email
        msg_text -- The email message in plain text format
        msg_html -- THe email message in HTML format
        login -- Login username to an email server
        password -- Password for the given username for login
        smtpserver -- SMTP server to use to send emails; default is GMail's
                      'smtp.gmail.com:587' address
    """

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = ','.join(to_addr_list)
    msg['Cc'] = ','.join(cc_addr_list)
    msg['Bcc'] = ','.join(bcc_addr_list)

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(unicode(msg_text).encode('utf-8'), 'plain')
    part2 = MIMEText(unicode(msg_html).encode('utf-8'), 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)
 
    server = smtplib.SMTP(smtpserver)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(login, password)

    server.sendmail(from_addr, to_addr_list, msg.as_string())
    server.quit()

def valid_image(img_url):
    """ Validates that the given URL is actually a valid image.
        Returns True if there's a valid image at the given URL, and False otherwise.

        img_url -- The URL of the possible image.
    """

    if (img_url is None or len(img_url) == 0):
        return False
    try:
        f = cStringIO.StringIO(urllib.urlopen(img_url).read())
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

    valid_url = None
    urls = []

    if (os.path.isfile(fname)):
        with open(fname, 'r') as f:
            urls = f.readlines()

    random.shuffle(urls)

    url = None
    while (not valid_image(url) and (len(urls) > 0)):
        url = urls.pop()

    # will empty file if len(urls) == 0
    with open(fname, 'w') as f:
        f.write('\n'.join(urls))

    return (valid_url)

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

def _send_neatza( tag, qotds, bash_data, img_url, to_addrs, email_data ):

    bash_fresh, bash_cache = bash_data
    email_addr, email_pass = email_data

    if (len(qotds) > 0):
        quote, qauth = qotds.pop()
    bash_text = ""
    if (len(bash_fresh) > 0):
        bash_id, bash_text = bash_fresh.pop()
        bash_cache.add(bash_id)

    subject = u'[%s] from neatza app' % strftime("%Y-%m-%d", gmtime())
    msg_text = (u'Random Quote Of The Day for %s\n%s\n%s' % (tag.title(), quote, qauth)) + \
               (u'\n\nRandom Bash.Org\n%s' % bash_text) + \
               (u'\n\n%s' % ( img_url ) )
    msg_html = (u'<div><b>Random Quote Of The Day for %s</b>' % (tag.title()) ) + \
               (u'<div style="margin-left: 30px; margin-top: 10px">') + \
               (u'%s<br/><b>%s</b></div></div>' % (quote, qauth) ) + \
               (u'<br/><br/>') + \
               (u'<div><b>Random Bash.Org</b><br />') + \
               (u'%s</div>' % bash_text) + \
               (u'<br/><br/>') + \
               (u'<img src="%s" style="max-width: 700px" >' % ( img_url ) )

    sendemail(from_addr    = email_addr,
              to_addr_list = to_addrs,
              cc_addr_list = [],
              bcc_addr_list = [],
              subject      = subject,
              msg_text     = msg_text,
              msg_html     = msg_html,
              login        = email_addr,
              password     = email_pass)

def main():
    qotds = get_qotds()

    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.readfp( open( os.path.join( APP_DIR, 'app.settings' ) ) )

    email_addr = config.get( 'mail', 'address' )
    email_pass = config.get( 'mail', 'password' )
    email_data = ( email_addr, email_pass )
    default_dst_addr = config.get ( 'mail', 'destination' )

    files_in_cnf_dir = os.listdir(CNF_DIR)
    random.shuffle( files_in_cnf_dir )
    bash_cache = bash.get_cache()
    bash_fresh = bash.get_randoms()
    bash_data = (bash_fresh, bash_cache)

    for fname in files_in_cnf_dir:
        if (not fname.endswith('.conf')):
            continue

        tag = fname[:-len('.conf')]

        to_addrs = _get_to_addrs(config, tag, default_dst_addr)
        if (len(to_addrs) == 0):
            continue

        full_fname = os.path.join( CNF_DIR, fname )
        url = extract_an_url( full_fname )

        if (url is None):
            log.warning("No image URL for '%s'", tag)

        _send_neatza( tag, qotds, bash_data, url, to_addrs, email_data )

    bash.save_cache (bash_cache)

if __name__ == "__main__":
    log.basicConfig(filename = os.path.join( LOG_DIR, 'neatza_app.log' ),
                    format   = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level    = log.INFO)
    try:
        main()
    except Exception as e:
        for line in traceback.format_exc().splitlines():
            log.error( line )

