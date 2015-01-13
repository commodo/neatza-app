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

import smtplib
from time import gmtime, strftime
import os
from PIL import Image
import urllib, cStringIO
import random
from BeautifulSoup import BeautifulSoup
import socket

import logging as log

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import traceback

import ConfigParser

APP_DIR = os.path.dirname(os.path.abspath(__file__))
CNF_DIR = os.path.join( APP_DIR, 'conf' )
LOG_DIR = os.path.join( APP_DIR, 'log' )

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

    fname = os.path.join(APP_DIR, fname)

    if (os.path.isfile(fname)):
        with open(fname, 'r') as f:
            urls = f.readlines()

    random.shuffle(urls)

    new_urls = []
    for url in urls:
        url = url.strip()
        if (url != ''):
            if (valid_url is None):# and (valid_image(url)):
                valid_url = url
            else:
                new_urls.append(url)

    with open(fname, 'w') as f:
        f.write('\n'.join(new_urls))

    return (valid_url)

def _get_eduro_com_qotds():
    """ Retrieve Quote Of The Day from eduro.com.
        The result is returned as a list of tuples of (quote_text, quote_author).
    """

    qotd_url = "http://www.eduro.com/"

    soup = BeautifulSoup( urllib.urlopen(qotd_url).read() )

    qotd_elem = soup.find( 'dailyquote' )

    quote = qauth = None
    quotd_sub_elems = qotd_elem.findAll('p')
    qotds = []
    if (len (quotd_sub_elems) == 2):
        qauth = quotd_sub_elems.pop().text.replace('&nbsp;', ' ').strip()
        quote = quotd_sub_elems.pop().text.replace('&nbsp;', ' ').strip()
        if (qauth[0] == '-'):
            qauth = qauth[1:].strip()
        if (qauth.startswith('&#8211;')):
            qauth = qauth[len('&#8211;') + 1:].strip()
        qotds.append( ( quote, qauth ) )

    return qotds


def _get_quotationspage_com_qotds():
    """ Retrieve Quote Of The Day from quotationspage.com.
        The result is returned as a list of tuples of (quote_text, quote_author).
    """

    qotd_url = "http://www.quotationspage.com/qotd.html"

    soup = BeautifulSoup( urllib.urlopen(qotd_url).read() )

    quotes = soup.findAll( 'dt', attrs = { 'class' : 'quote' } )
    qauths = soup.findAll( 'dd', attrs = { 'class' : 'author' } )

    qotds = []
    for quote, qauth in zip(quotes, qauths):
        qauth_text = qauth.text
        idx = qauth_text.find('&nbsp;')
        if (idx > -1):
            qauth_text = qauth_text[:idx]
        qotds.append( (quote.text, qauth_text) )

    return qotds

def _get_quotes_daddy():

    qotd_url = "http://www.quotesdaddy.com/"

    soup = BeautifulSoup( urllib.urlopen(qotd_url).read() )

    divs = soup.findAll( 'div' )
    quoteObjects = [ div for div in divs if div.get('class') and div['class'].find('quoteObject') > -1 ]
    #;soup.findAll( 'div', attrs = { 'class' : 'quoteObject' } )

    quote = qauth = None
    qotds = []
    idx = 0
    for qObj in quoteObjects:
        idx += 1
        if (idx == 2):
            continue
        qauth = qObj.find( 'div', attrs = { 'class' : 'quoteAuthorName' } ) \
                .text.replace('&nbsp;', ' ').strip()
        quote = qObj.find( 'div', attrs = { 'class' : 'quoteText' } ) \
                .text.replace('&nbsp;', ' ').strip().replace( '&rdquo;', '' ).replace( '&ldquo;', '' )
        qotds.append( ( quote, qauth ) )

    return qotds

QOTD_SERVERS = [
    #( 'djxmmx.net',             17, 'Each Request'),
    #( 'qotd.nngn.net',          17, 'Daily'),
    #( 'qotd.atheistwisdom.com', 17, 'Daily'),
    #( 'ota.iambic.com',         17, 'Each Request'),
    #( 'alpha.mike-r.com',       17, 'Each Request'),
    #( 'electricbiscuit.org',    17, 'Each Request'),
]

MAX_MSG_LEN = 20000

def _get_qotd_from_server(server_idx = 0):
    """ Retrieve Quote Of The Day from a server that has QTOD service.
        The result is returned as a tuple of (quote_text, quote_author).
    """

    ret = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        qotd_server = QOTD_SERVERS[server_idx][:-1]
        s.connect( qotd_server )
        s.settimeout( 3 )

        message = s.recv( MAX_MSG_LEN )
        s.close()

        msg_parts = message.strip().split('\n')
        if (len(msg_parts) > 1):
            quote, qauth = msg_parts[0].strip(), msg_parts[1].strip()
            if (quote[0] == '"'):
                quote = quote[1:]
            if (quote[-1] == '"'):
                quote = quote[:-1]
            if (qauth.endswith('\r\x00')):
                qauth = qauth[:-2]

            if (len (qauth) > 0):
                if (qauth[0] == '-'):
                    qauth = qauth[1:].strip()
                else:
                    quote = quote + ' ' + qauth
                    qauth = ''

            ret = (quote, qauth)
    except:
        ret = None

    return (ret)

def _get_goodreads_qotds():

    qotd_url = "http://www.goodreads.com/quotes_of_the_day"

    soup = BeautifulSoup( urllib.urlopen(qotd_url).read() )

    quoteTexts = soup.findAll( 'div', attrs = { 'class' : 'quoteText' } )

    qotds = []
    for quoteText in quoteTexts:
        qts = quoteText.text.split('&#8213;')
        quote = qts[0].replace('&ldquo;','').replace('&rdquo;','')
        qauth = qts[1]
        qotds.append( (quote, qauth) )

    return qotds

def get_qotds():
    """ Retrieve a random Quote Of The Day.
        The result is returned as a list of tuples of (quote_text, quote_author).
    """
    qotds = _get_quotationspage_com_qotds() + _get_eduro_com_qotds() + \
            _get_goodreads_qotds() + _get_quotes_daddy()
    for qotd_server_idx in range ( len ( QOTD_SERVERS ) ):
        qotd = _get_qotd_from_server ( qotd_server_idx )
        if (qotd is not None):
            qotds.append( qotd )

    random.shuffle( qotds )

    return (qotds)

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


def main():
    qotds = get_qotds()

    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.readfp( open( os.path.join( APP_DIR, 'app.settings' ) ) )

    email_addr = config.get( 'mail', 'address' )
    email_pass = config.get( 'mail', 'password' )
    default_dst_addr = config.get ( 'mail', 'destination' )

    files_in_cnf_dir = os.listdir(CNF_DIR)
    random.shuffle( files_in_cnf_dir )

    for fname in files_in_cnf_dir:

        url = None
        full_fname = os.path.join( CNF_DIR, fname )
        if (fname.endswith('.conf')):
            url = extract_an_url( full_fname )

        if (url is None):
            continue

        tags = [ fname[:-len('.conf')] ]
        if (len(qotds) > 0):
            quote, qauth = qotds.pop()

        for tag in tags:
            subject = u'[%s] from neatza app' % strftime("%Y-%m-%d", gmtime())
            msg_text = (u'Random Quote Of The Day for %s\n%s\n%s' % (tag.title(), quote, qauth)) + \
                       (u'\n\n%s' % ( url ) )
            msg_html = (u'<div><b>Random Quote Of The Day for %s</b>' % (tag.title()) ) + \
                       (u'<div style="margin-left: 30px; margin-top: 10px">') + \
                       (u'%s<br/><b>%s</b></div></div>' % (quote, qauth) ) + \
                       (u'<br/><br/>') + \
                       (u'<img src="%s" style="max-width: 700px" >' % ( url ) )

            to_addrs = _get_to_addrs(config, tag, default_dst_addr)
            if (len(to_addrs) > 0):
                sendemail(from_addr    = email_addr,
                          to_addr_list = to_addrs,
                          cc_addr_list = [],
                          bcc_addr_list = [],
                          subject      = subject,
                          msg_text     = msg_text,
                          msg_html     = msg_html,
                          login        = email_addr, 
                          password     = email_pass)

if __name__ == "__main__":
    log.basicConfig(filename = os.path.join( LOG_DIR, 'neatza_app.log' ),
                    format   = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level    = log.INFO)
    try:
        main()
    except Exception as e:
        for line in traceback.format_exc().splitlines():
            log.error( line )

