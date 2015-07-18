# coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..')
import time
import bs4
from selenium import webdriver
import traceback
from utils import browser_open
import logging as log

# for any results page, the web driver scrolls down until the number of
# results reaches the limit (limit is 500 or 1000 depending on time of day...)
#for now, get users for a query
def process_whole_page(driver, url, process, limit=500,
                       connections_to_attempt=3, scrolls_to_attempt=3,
                       sleep_interval=2):
    """
    Process the whole page at url with the given function, making sure
    that at least limit results have been processed -- or that there
    are less than limit results on the page.
    To do this, we scroll down the page with driver.

    Parameters
    ----------
    driver: selenium.webdriver
    url: string
    process: function
        Text fetched by driver is processed by this.
        Returns a list.
    limit: int
        Until we get this many results, or become certain that there
        aren't this many results at the url, we will keep scrolling the
        driver.
    connections_to_attempt: int
    scrolls_to_attempt: int
    sleep_interval: float
        Sleep this number of seconds between tries.

    Returns
    -------
    results: list or None
        Whatever the process function returns.

    Raises
    ------
    e: Exception
        If connection times out more than connections_to_attempt
    """
    assert(scrolls_to_attempt > 0)
    assert(limit > 0)
    connections_attempted = 0
    while connections_attempted < connections_to_attempt:
        try:
            driver.get(url)
            soup = bs4.BeautifulSoup(driver.page_source)
            results = process(soup)
            all_scrolls_attempted = 0

            # If we fetch more than limit results already, we're done.
            # Otherwise, try to get more results by scrolling.
            # We give up after some number of scroll tries.
            # If we do get more results, then the scroll count resets.
            if len(results) < limit:
                scrolls_attempted = 0
                while (scrolls_attempted < scrolls_to_attempt and
                       len(results) < limit):
                    all_scrolls_attempted += 1
                    scrolls_attempted += 1

                    # Scroll and parse results again.
                    # The old results are still on the page, so it's fine
                    # to overwrite.
                    driver.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight);")
                    soup = bs4.BeautifulSoup(driver.page_source)
                    new_results = process(soup)

                    if len(new_results) > len(results):
                        results = new_results
                        scrolls_attempted = 0

            log.info('Obtained %d results after %d scrolls' % (
                len(results), all_scrolls_attempted))
            if len(results) > limit:
                results = results[:limit]
            return results

        except Exception as e:
            connections_attempted += 1
            log.error('URL failed: {}'.format(url))
            log.error('  connections attempted: {}'.format(connections_attempted))
            log.error('  exception message: {}'.format(e))
            traceback.print_exc()
            time.sleep(sleep_interval)

    log.info('URL skipped: {}'.format(url))
    return None


def parse_board_object(board, username, source):
    """
    Parameters
    ----------
    board: some kind of bs4 object

    Returns
    -------
    data: dict
    """
    num_pins = board.select('.boardPinCount')[0].text.strip()
    num_pins = num_pins.split(' ')[0].replace(',', '')
    data = {
        'username': username,
        'source': source,
        'board_url': 'www.pinterest.com{}'.format(
            board.find_all('a', {'class': 'boardLinkWrapper'})[0].get('href')),
        'board_name': board.select('.boardName .title')[0].text.strip(),
        'cover_img': board.select('img')[0]['src'],
        'thumb_imgs': [_['src'] for _ in board.select('img')[1:]],
        'num_pins': int(num_pins)
    }
    data['_id'] = data['board_url']
    return data


def scrape_user_boards(driver, username, source):
    """
    Return all boards of the user.

    Parameters
    ----------
    username: string
    source: string
        Describes why this user's boards are getting scraped:
        - "query: <whatever>"
        - "follower of: <username>"

    Returns
    -------
    boards: list of dicts
    """
    url = 'http://www.pinterest.com/{}/boards/'.format(username)
    boards = process_whole_page(
        driver, url, lambda soup: [
            parse_board_object(board, username, source)
            for board in soup.select('div.item')
        ])
    return boards


def get_followers_list(user_url, driver, followers=True):
    """
    Returns a list of users who follow or are followed by a user.

    Parameters
    ----------
    user_url: string
    driver: selenium.webdriver
    followers: bool
        If True, gets users who are followers of this user.
        If False, gets users who this user follows.
    """
    if followers:
        url = user_url + '/followers/'
    else:
        url = user_url + '/following/'
    process = lambda soup: [
        str(item.find_all('a',
            {'class': 'userWrapper'})[0].get('href'))
        for item in soup.select('div.item')
    ]

    followers = process_whole_page(driver, url, process)
    return followers


def get_usernames_from_query_results_page(driver, url, limit=500):
    # Parse the usernames, which exist as the last part of hrefs in
    # .boardLinkWrapper <a> tags.
    get_usernames = lambda soup: [
        link['href'].split('/')[1]
        for link in soup.findAll('a', {'class': 'boardLinkWrapper'})
    ]
    usernames = process_whole_page(driver, url, get_usernames, limit)
    return usernames


def scrape_boards(query, board_collection, user_collection, user_limit=500):
    """
    Find all users with a board matching the query, and scrape all of
    their boards, inserting them into board_collection.

    If user is already present in user_collection, it means that we
    have scraped their boards, and so do not need to scrape again -- but
    do need to update their record with this query.
    """
    log.info(u'scrape_boards: on {}'.format(query))

    driver = browser_open()
    url = 'http://www.pinterest.com/search/boards/?q=' + query
    usernames = get_usernames_from_query_results_page(driver, url, user_limit)

    # For each user, scrape their boards page, or update their record.
    for username in usernames:
        # If we've already scraped this user's boards, then we don't
        # need to do that again, but we note that we have seen this
        # user for this new query.
        username_count = user_collection.find(
            {'username': username}).limit(1).count()
        if username_count > 0:
            # TODO: confirm that this appends to list of queries
            # because it looks like it just overwrites it
            if query in user_collection.find_one(
                    {'username': username})['query']:
                log.info('Already ran query {} for user {}'.format(
                    query, username))
            else:
                log.info("Already ran a different query for user {}".format(
                    username))
                user_collection.update(
                    {'username': username}, {'$push': {'query': query}})

        # Otherwise, we scrape the user's boards.
        else:
            boards = scrape_user_boards(
                driver, username, 'query: {} '.format(query))
            if len(boards) > 0:
                user_collection.insert({
                    'username': username,
                    'num_boards': len(boards),
                    'query': [query]
                })
                for board in boards:
                    try:
                        board_collection.insert(board)
                    except pymongo.errors.DuplicateKeyError:
                        continue
                log.info('Inserted {} from {} with query: {}'.format(
                    len(boards), username, query))


def get_boards(driver, query):
    """
    Given a query, return the list of boards dicts that show up.
    """
    url = 'http://www.pinterest.com/search/boards/?q=' + query
    boards = process_whole_page(
        driver, url, lambda soup: [
            parse_board_page(board, query)
            for board in soup.select('div.item')
        ])
    return boards

#source: url it was pinned from
#img: largest resolution is 736x for all images it seems
def parse_pin(pin, username, board_name, query):
    #from IPython import embed
    #embed()
    pinned_from = pin.select('h4.pinDomain')
    repins = pin.select('em.socialMetaCount')
    if len(repins) == 0:
        repins = 0
    else:
        repins = int(repins[0].text.strip())
    if len(pinned_from) == 0:
        pinned_from = username
    else:
        pinned_from = pinned_from[0].text.strip()
    caption = pin.select('img')[0]
    try:
        caption = caption['alt']
    except Exception:
        caption = ''
    data = {
        'username': username,
        'pin_url': 'www.pinterest.com{}'.format(
            pin.find('a', {'class': 'pinImageWrapper'}).get('href')),
        'repins_likes_url': ['www.pinterest.com{}'.format(
            link['href']) for link in pin.select('a.socialItem')],
        'caption': caption,
        'source': pinned_from,
        'img': pin.select('img')[0]['src'].replace('236x', '736x'),
        'repins': repins,
        'board_name': board_name,
        'query': [query]
    }
    data['_id'] = data['pin_url']
    return data


def parse_board_page(board, query):
    url = board.find_all('a', {'class': 'boardLinkWrapper'})[0].get('href')
    data = {
        'username': url.split('/')[1],
        'board_url': 'http://www.pinterest.com{}'.format(url),
        'board_name': url.split('/')[2],
        'query': query
    }
    return data


def scrape_pins(driver, board, pin_collection):
    url = board['board_url']
    driver.get(url)

    pins = process_whole_page(
        driver, url, lambda soup: [parse_pin(
            pin, board['username'], board['board_name'], board['query'])
            for pin in soup.select('div.item')
        ])
    for pin in pins:
        if pin_collection.find({'_id': pin['_id']}).count() == 0:
            pin_collection.insert(pin)
            log.info('Inserted {} from board {}: {}'.format(
                pin['pin_url'], board['board_url'], board['query']))
        else:
            log.info('{} has already been added'.format(pin['pin_url']))
            pin_collection.update(
                {'pin_url': pin['pin_url']},
                {'$push': {'query': board['query']}}
            )

# Main

def get_followers(username):
    """
    Get followers for user
    """
    url = 'http://www.pinterest.com/%s' % (username)
    followers = get_followers_list(url, driver)
    following = get_followers_list(url, driver, False)
    log.info('Updated %s. Followers: %d  Following: %d' % (
            username, len(followers), len(following)))
    return followers, following

# FIXME: simplify later this
def get_boards(match, username):
    user_collection = { "username" : usernmae }
    board_collection = []
    scrape_boards(match, board_collection, user_collection)


def get_pinss(db, queries):
    pin_collection = db['pins']
    driver = browser_open()
    for query in queries:
        board_iterator = get_boards(driver, query)
        for board in board_iterator:
            doc = {
                'board_name': board['board_name'],
                'username': board['username']
            }
            if vislab.util.zero_results(pin_collection, doc):
                log.info("Scraping: {}".format(board['board_url']))
                t = time.time()
                scrape_pins(driver, board, pin_collection)
                log.info("...took {:.2f} s".format(time.time() - t))
            else:
                log.info("Not scraping {}".format(doc))
        log.info('Done scraping pins for {}'.format(query))

"""
if __name__ == '__main__':
    print("usage: scrape.py <mode>")
    assert(len(sys.argv) == 2)
    mode = sys.argv[1]

    if mode == 'followers':
        get_followers(db)

    elif mode == 'boards':
        get_boards_for_queries(db, queries)

    elif mode == 'pins':
        get_pins_for_queries(db, queries)

    else:
        raise ValueError("Invalid mode")
"""

