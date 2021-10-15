import codecs as _codecs
import re as _re
import sys as _sys
import time as _time
from random import random as _random, randrange as _randrange
from urllib.parse import urlparse as _urlparse
from bs4 import BeautifulSoup as _Soup
from chardet.universaldetector import UniversalDetector as _UniversalDetector
from mechanize import Browser as _Browser, BrowserStateError as _BrowserStateError, Link as _Link
from .exceptions import MechSpiderError as _MechSpiderError
from .group import Group as _Group


_CharsetDetector = _UniversalDetector()


# pylint: disable=invalid-name
def Soup(*args, **kwargs):
  return _Soup(*args, features='html5lib', **kwargs)


# pylint: disable=too-many-instance-attributes
class MechSpider:
  RE_CHARSET_SEARCHER = _re.compile(r'charset=[\'"]?([^,; ]+)[\'"]?')

  def __init__(self):
    self._visit_groups = []

    self.browser = _Browser()
    self.browser.set_handle_equiv(True)
    self.browser.set_handle_gzip(True)
    self.browser.set_handle_redirect(True)
    self.browser.set_handle_referer(True)
    if hasattr(self, 'USER_AGENT'):
      self.browser.set_header('User-Agent', self.USER_AGENT)
    if hasattr(self, 'HANDLE_ROBOTS'):
      self.browser.set_handle_robots(self.HANDLE_ROBOTS)

    # Make first `follow_link()` works
    self.browser.set_html('', url='file:///usr/share/MechSpider/www/mainpage.html')

    self.home_page = self.HOME_PAGE \
      if hasattr(self, 'HOME_PAGE') else None

    self.random_visit = self.RANDOM_VISIT \
      if hasattr(self, 'RANDOM_VISIT') else False

    self.random_wait = self.RANDOM_WAIT \
      if hasattr(self, 'RANDOM_WAIT') else False
    self.random_wait_factor = self.RANDOM_WAIT_FACTOR \
      if hasattr(self, 'RANDOM_WAIT_FACTOR') else 1

    self.use_chardet = self.USE_CHARDET \
      if hasattr(self, 'USE_CHARDET') else False
    self.chardet_line_limit = self.CHARDET_LINE_LIMIT \
      if hasattr(self, 'CHARDET_LINE_LIMIT') else 128

    self.enable_debug = self.ENABLE_DEBUG \
      if hasattr(self, 'ENABLE_DEBUG') else False

  @classmethod
  # pylint: disable=unused-argument
  def pattern(cls, pattern_):  # WTF?
    def _(handler):
      assert cls is not MechSpider
      if not hasattr(cls, 'Patterns'):
        cls.Patterns = {}

      nonlocal pattern_
      if isinstance(pattern_, str):
        pattern_ = _re.compile(pattern_)
      cls.Patterns[pattern_] = handler
    return _

  def _detect_encoding(self, response):
    response.seek(0, 0)
    _CharsetDetector.reset()

    line_count = 0
    while line_count < self.chardet_line_limit:
      _CharsetDetector.feed(response.readline())
      if _CharsetDetector.done:
        break
      line_count += 1
    _CharsetDetector.close()
    return _CharsetDetector.result['encoding']

  @classmethod
  def _get_encoding(cls, response, fallback_encoding='utf-8'):
    encoding = fallback_encoding
    for content_type in response.info().getheaders('Content-Type'):
      matched = cls.RE_CHARSET_SEARCHER.search(content_type)
      if matched:
        encoding = matched.group(1)
        try:
          _codecs.lookup(encoding)
          break
        except LookupError:
          pass
    return encoding

  @staticmethod
  def _is_absolute_url(url):
    result = _urlparse(url)
    return bool(result.scheme and result.netloc)

  @classmethod
  def _url_to_link(cls, url):
    assert cls._is_absolute_url(url)
    return _Link(url, '', '', 'a', [('href', '')])

  @staticmethod
  def _link_to_url(link):
    return link.absolute_url

  def _get_index(self, indexable):
    length = len(indexable)
    index = length - 1
    if self.random_visit:
      index = _randrange(0, length)
    return index

  def _debug(self, message):
    if self.enable_debug is True:
      _sys.stdout.write('DEBUG: ' + message + '\n')

  def _visit(self, url_or_link, method):
    self._debug('visiting ' + repr(url_or_link))

    url = url_or_link
    link = url_or_link
    if isinstance(url_or_link, str):
      link = self._url_to_link(url_or_link)
    elif isinstance(url_or_link, _Link):
      url = self._link_to_url(url_or_link)
    else:
      raise _MechSpiderError('Unknown visit object')

    # pylint: disable=consider-using-dict-items
    for pattern in self.Patterns:
      if pattern.match(url):
        self._debug(repr(url) + ' wanted by ' + repr(pattern))

        handler = self.Patterns[pattern]

        if method is _Group.VISIT_METHOD_OPEN:
          self._debug('visit method is \'open\'')
          # pylint: disable=assignment-from-none
          response = self.browser.open(url)  # WTF? x2
        elif method is _Group.VISIT_METHOD_FOLLOW:
          self._debug('visit method is \'follow\'')
          # pylint: disable=assignment-from-none
          response = self.browser.follow_link(link)  # WTF? x3
        else:
          raise _MechSpiderError('Unknown visit method')

        if self.use_chardet is True:
          encoding = self._detect_encoding(response)
        else:
          encoding = self._get_encoding(response)
        self._debug('spider thinks encoding is ' + repr(encoding))

        markup = response.get_data().decode(encoding)
        soup = Soup(markup)
        handler(self, soup)

        if self.random_wait:
          _time.sleep(self.random_wait_factor * _random())
        break

  def create_group(self, unrelated=False):
    group = _Group()
    if unrelated is True:
      group.method = _Group.VISIT_METHOD_OPEN
    self._visit_groups.append(group)
    return group

  def start(self):
    if self.home_page:
      group = self.create_group(unrelated=True)
      group.append(self.home_page)

    while self._visit_groups:
      visit_group = self._visit_groups[-1]
      if visit_group:
        index = self._get_index(visit_group)
        url_or_link = visit_group.pop(index)
        self._visit(url_or_link, method=visit_group.method)
      else:
        if self.browser.request:
          self._debug('closing ' + repr(self.browser.geturl()))
          self._visit_groups.pop()
        else:
          # Default page which has set by `set_html()`, it has no `request`
          # property, it means we have already reached the last page
          break  # And it is often occurrs when your `home_page` mismatched

        # Well, the `history` doesn't public yet, and it has no `__len__()`,
        # so we just make it simply
        try:
          self.browser.back()
        except _BrowserStateError:
          break
