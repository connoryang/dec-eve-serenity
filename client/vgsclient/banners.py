#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\vgsclient\banners.py
import requests
import collections
import logging
from xml.etree import ElementTree
from eveexceptions.exceptionEater import ExceptionEater
log = logging.getLogger(__name__)
BANNER_FEED_LANGUAGE_CODES = {'EN': 'en-us',
 'DE': 'de-de',
 'RU': 'ru-ru'}
BANNER_FEED_URL = 'http://newsfeed.eveonline.com/%(languageCode)s/%(channelId)s/articles'
BANNER_FEED_NAMESPACES = {'atom': 'http://www.w3.org/2005/Atom',
 'media': 'http://search.yahoo.com/mrss/',
 'ccpmedia': 'http://ccp/media'}

def GetBanners(languageID, region, channelID):
    feedUrl = _GetBannerFeedUrl(languageID, region, channelID)
    try:
        resp = requests.get(feedUrl)
    except requests.RequestException as e:
        log.warn('GetBanners failed to GET feed from %s: %s', feedUrl, e)
        return []

    if resp.status_code != 200:
        log.warn('GetBanners could not read from banner feed %s - Error code:%s', feedUrl, resp.status_code)
        return []
    banners = _ParseBannerFeed(resp.text)
    return banners


def _GetBannerFeedUrl(languageID, region, channelID):
    if region == 'optic':
        url = 'http://eve.tiancity.com/client'
    else:
        languageCode = BANNER_FEED_LANGUAGE_CODES.get(languageID, BANNER_FEED_LANGUAGE_CODES['EN'])
        url = BANNER_FEED_URL % {'languageCode': languageCode,
         'channelId': channelID}
    return url


def _ParseBannerFeed(feed):
    root = ElementTree.fromstring(feed)
    banners = []
    for element in root.findall('atom:entry', namespaces=BANNER_FEED_NAMESPACES):
        with ExceptionEater('Failed to parse store banner element'):
            descriptionElement = element.find('ccpmedia:group/ccpmedia:description', namespaces=BANNER_FEED_NAMESPACES)
            action = descriptionElement.text
            imageElement = element.find('ccpmedia:group/ccpmedia:content', namespaces=BANNER_FEED_NAMESPACES)
            imageUrl = imageElement.attrib['url']
            banners.append((imageUrl, action))

    return banners
