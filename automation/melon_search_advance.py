# coding: utf-8
import os
from os.path import abspath, basename, dirname, exists, join
import sys
import re
import json
import urllib
import urllib2
import time
import unicodedata

def get(url):
    opener = urllib2.build_opener()
    opener.addheaders = [
        ('User-agent', 'Mozilla/5.0 (compatible; MSIE 10.6; Windows NT 6.1; Trident/5.0; InfoPath.2; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 2.0.50727) 3gpp-gba UNTRUSTED/1.0'),
        ('Referer', 'http://www.melon.com'),
    ]
    try:
        return opener.open(url).read()
    except urllib2.HTTPError:
        return None

def check_icon(icon_url):
    icon_path = abspath(join(dirname(__file__), 'caches', 'melon', basename(icon_url)))
    if not exists(icon_path):
        if not exists(dirname(icon_path)):
            os.makedirs(dirname(icon_path))

        image_bin = get(icon_url)
        if image_bin:
            open(icon_path, 'wb').write(image_bin)
    return icon_path


def safe_print(s):
    if isinstance(s, unicode):
        print(s.encode('utf-8'))
    else:
        print(s)


class Melon(object):
    def __init__(self, query):
        if isinstance(query, unicode):
            query = query.encode('utf8')

        params = urllib.urlencode({
                'jscallback': 'jQuery19106274424700532109_{}'.format(int(time.time())),
                'query': query,
                '_': str(int(time.time())),
            })
        url = "http://www.melon.com/search/keyword/index.json?" + params

        # print(url)

        bin = get(url)

        bin = re.sub(r'^[a-zA-Z0-9_]+\(', '', bin)
        bin = re.sub(r'\);', '', bin)
        bin = re.sub(r'<\/?b>', '', bin)

        response = json.loads(bin)

        # print(response)

        self.status = response['STATUS']
        self.keyword = response.get('KEYWORD', [])
        self.https_domain = response['httpsDomain']
        self.http_domain = response['httpDomain']
        self.static_domain = response['staticDomain']

        self.artists = [Artist(self.static_domain, meta) for meta in response.get("ARTISTCONTENTS", [])]
        self.albums = [Album(self.static_domain, meta) for meta in response.get("ALBUMCONTENTS", [])]
        self.songs = [Song(self.static_domain, meta) for meta in response.get("SONGCONTENTS",[])]

        # [Keyword(meta) for meta in response["KEYWORDCONTENTS"]]


class Artist(object):
    def __init__(self, static_domain, meta):
        self.id               = meta['ARTISTID']
        self.nationality_name = meta['NATIONALITYNAME']
        self.image_url        = static_domain + meta['ARITSTIMG']
        self.name             = meta['ARTISTNAME']
        self.name_dp          = meta['ARTISTNAMEDP']
        self.sex              = meta['SEX']
        self.acttype_names    = meta['ACTTYPENAMES']
        self.url = 'http://www.melon.com/artist/timeline.htm?artistId={}'.format(self.id)

    def xml(self):
        return u'''<item uid="%(id)s" arg="%(url)s" valid="yes" autocomplete="yes">
    <title>%(name)s</title>
    <subtitle>[Artist] %(nationality_name)s</subtitle>
    <icon>%(icon_path)s</icon>
</item>''' % {
            'id': self.id,
            'url': self.url,
            'name': u'{} ({}, {})'.format(self.name, self.acttype_names, self.sex),
            'nationality_name': self.nationality_name,
            'icon_path': check_icon(self.image_url),
        }


class Album(object):
    def __init__(self, static_domain, meta):
        self.id          = meta['ALBUMID']
        self.image_url   = static_domain + meta['ALBUMIMG']
        self.name        = meta['ALBUMNAME']
        self.name_dp     = meta['ALBUMNAMEDP']
        self.artist_name = meta['ARTISTNAME']
        self.url         = 'http://www.melon.com/album/detail.htm?albumId={}'.format(self.id)

    def xml(self):
        return u'''<item uid="%(id)s" arg="%(url)s" valid="yes" autocomplete="yes">
    <title>%(name)s</title>
    <subtitle>[Album] %(artist_name)s</subtitle>
    <icon>%(icon_path)s</icon>
</item>''' % {
            'id': self.id,
            'url': self.url,
            'name': self.name,
            'artist_name': self.artist_name,
            'icon_path': check_icon(self.image_url),
        }

class Song(object):
    def __init__(self, static_domain, meta):
        self.id             = meta['SONGID']
        self.name_dp        = meta['SONGNAMEDP']
        self.name           = meta['SONGNAME']
        self.album_id       = meta['ALBUMID']
        self.album_name     = meta['ALBUMNAME']
        self.album_image_url  = static_domain + meta['ALBUMIMG']
        self.artist_name    = meta['ARTISTNAME']
        self.url = 'http://www.melon.com/song/detail.htm?songId={}'.format(self.id)

        params = urllib.urlencode({
            'contsType': 'S',
            'menuId': '29010101',
            'playSongs': self.id,
            'timer': str(time.time()),
            })
        # self.url = 'http://wplay.melon.com/webplayer/index.htm?' + params

    def xml(self):
        return u'''<item uid="%(id)s" arg="%(url)s" valid="yes" autocomplete="yes">
    <title>%(name)s</title>
    <subtitle>[Song] %(album_name)s</subtitle>
    <icon>%(icon_path)s</icon>
</item>''' % {
            'id': self.id,
            'url': self.url,
            'name': self.name,
            'album_name': self.album_name,
            'icon_path': check_icon(self.album_image_url),
        }


class Keyword(object):
    def __init__(self, meta):
        self.keyword_dp = meta['KEYWORDDP']
        self.keyword    = meta['KEYWORD']


if __name__ == '__main__':
    q = sys.argv[1].decode('utf8')
    q = unicodedata.normalize('NFC', q)

    melon = Melon(q)

    rows = melon.artists + melon.albums + melon.songs

    safe_print(u'<?xml version="1.0" encoding="utf-8"?>')
    safe_print(u'<items>')
    for row in rows:
        safe_print(row.xml())
    safe_print(u'</items>')

