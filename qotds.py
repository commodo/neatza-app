
import urllib
import random
import socket
from bs4 import BeautifulSoup

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

