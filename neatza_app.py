#!/usr/bin/env python 

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

import logging

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import ConfigParser

APP_DIR = os.path.dirname(os.path.abspath(__file__))

# When email fails https://support.google.com/mail/answer/14257

def sendemail(from_addr, to_addr_list, cc_addr_list,
              subject, msg_text, msg_html,
              login, password,
              smtpserver='smtp.gmail.com:587'):

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = ','.join(to_addr_list)
    msg['Cc'] = ','.join(cc_addr_list)

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(msg_text, 'plain')
    part2 = MIMEText(msg_html, 'html')

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

def validate_is_image(img_url):
    """ Validates that the given URL is actually a valid image.
        Returns True if there's a valid image at the given URL, and False otherwise.

        img_url -- The URL of the possible image.
    """

    try:
        f = cStringIO.StringIO(urllib.urlopen(img_url).read())
        Image.open(f)
        return True
    except:
        return False

def extract_an_url(fname):
    """ Extracts from a filename the list of senders to which to send a
        URL from a file.

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
            if (valid_url is None) and (validate_is_image(url)):
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

QOTD_SERVERS = [
    ( 'djxmmx.net',             17, 'Each Request'),
    #( 'qotd.nngn.net',          17, 'Daily'),
    #( 'qotd.atheistwisdom.com', 17, 'Daily'),
    #( 'ota.iambic.com',         17, 'Each Request'),
    ( 'alpha.mike-r.com',       17, 'Each Request'),
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


def get_qotds():
    """ Retrieve a random Quote Of The Day.
        The result is returned as a list of tuples of (quote_text, quote_author).
    """
    qotds = _get_quotationspage_com_qotds() + _get_eduro_com_qotds()
    for qotd_server_idx in range ( len ( QOTD_SERVERS ) ):
        qotd = _get_qotd_from_server ( qotd_server_idx )
        if (qotd is not None):
            qotds.append( qotd )

    random.shuffle( qotds )

    return (qotds)


def main():
    qotds = get_qotds()

    messages = {}
    for fname in os.listdir(APP_DIR):
        if (fname.endswith('.conf')):
            tag = fname[:-len('.conf')]

            if (len(qotds) > 0):
                quote, qauth = qotds.pop()

            subject = u'[%s] from neatza app' % strftime("%Y-%m-%d", gmtime())
            msg_text = u'Random Quote Of The Day for %s\n%s\n%s' % (tag.title(), quote, qauth)
            msg_html = (u'<div><b>Random Quote Of The Day for %s</b>' % (tag.title()) ) + \
                       (u'<div style="margin-left: 30px; margin-top: 10px">') + \
                       (u'%s<br/><b>%s</b></div></div>' % (quote, qauth) )

            full_fname = os.path.join( APP_DIR, fname )
            url = extract_an_url( full_fname )
            if (url):
                msg_text += u'\n\n%s' % ( url )
                msg_html += (u'<br/><br/>') + \
                     (u'<img src="%s" style="max-width: 700px" >' % ( url ) )

            messages[tag] = (subject, msg_text, msg_html)

    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.readfp( open( os.path.join( APP_DIR, 'app.settings' ) ) )

    email_addr = config.get( 'mail', 'address' )
    email_pass = config.get( 'mail', 'password' )
    email_dest_addr = config.get ( 'mail', 'destination' )

    subscription_map = { email_dest_addr : messages.values() }

    for to_addr, messages in subscription_map.items():
        for subject, msg_text, msg_html in messages:
            sendemail(from_addr    = email_addr,
                      to_addr_list = [ to_addr ],
                      cc_addr_list = [], 
                      subject      = subject,
                      msg_text     = msg_text,
                      msg_html     = msg_html,
                      login        = email_addr, 
                      password     = email_pass)

if __name__ == "__main__":
    logging.basicConfig(filename=os.path.join( APP_DIR, 'neatza_app.log' ), level=logging.INFO)
    try:
        main()
    except Exception as e:
        logging.error( str(e) )

