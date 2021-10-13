import re as _re
import time as _time
from bs4 import BeautifulSoup as _Soup
from chardet.universaldetector import UniversalDetector as _UniversalDetector
from mechanize import Browser as _Browser, Link as _Link
from random import random as _random, randrange as _randrange
from .exceptions import PropertyMissingError as _PropertyMissingError


_CharsetDetector = _UniversalDetector()


# pylint: disable=invalid-name
def Soup(*args, **kwargs):
  return _Soup(*args, features='html5lib', **kwargs)


# pylint: disable=too-many-instance-attributes
class MechSpider:
  def __init__(self):
    self.visit_queue = []
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

    self.max_visit_count = self.MAX_VISIT_COUNT \
      if hasattr(self, 'MAX_VISIT_COUNT') else 0xffff
    self.visited_count = 0

    self.random_visit = self.RANDOM_VISIT \
      if hasattr(self, 'RANDOM_VISIT') else False

    self.random_wait = self.RANDOM_WAIT \
      if hasattr(self, 'RANDOM_WAIT') else False
    self.random_wait_factor = self.RANDOM_WAIT_FACTOR \
      if hasattr(self, 'RANDOM_WAIT_FACTOR') else 1

  @classmethod
  # pylint: disable=unused-argument
  def pattern(cls, pattern_):  # WTF?
    def _(callback):
      if not hasattr(cls, 'Patterns'):
        cls.Patterns = {}

      nonlocal pattern_
      if isinstance(pattern_, str):
        pattern_ = _re.compile(pattern_)
      cls.Patterns[pattern_] = callback
    return _

  @staticmethod
  def detect_encoding(response, max_line_count=64):
    response.seek(0, whence=0)
    _CharsetDetector.reset()

    line_count = 0
    while line_count < max_line_count:
      _CharsetDetector.feed(response.readline())
      if _CharsetDetector.done:
        break
      line_count += 1
    _CharsetDetector.close()
    return _CharsetDetector.result['encoding']

  @staticmethod
  def url_to_link(url):
    # XXX: is that safe?
    return _Link(base_url=url, url='', text='', tag='a', attrs=[])

  def visit(self, link):
    if isinstance(link, str):
      link = self.url_to_link(link)

    # pylint: disable=consider-using-dict-items
    for pattern in self.Patterns:
      if pattern.match(link.absolute_url) is not None:
        callback = self.Patterns[pattern]
        # pylint: disable=assignment-from-none
        response = self.browser.follow_link(link)  # WTF? x2
        encoding = self.detect_encoding(response)
        markup = response.get_data().decode(encoding)
        soup = Soup(markup=markup)
        callback(soup, self)

        if self.random_wait:
          _time.sleep(self.random_wait_factor * _random())

        self.visited_count += 1
        if self.visited_count > self.max_visit_count:
          back_step = _randrange(0, self.max_visit_count)
          self.browser.back(back_step)
          self.visited_count -= back_step
        break

  def start(self):
    if self.home_page is None:
      raise _PropertyMissingError('HOME_PAGE missing')
    link = self.url_to_link(self.home_page)
    self.visit(link)

    if self.random_visit:
      while True:
        length = len(self.visit_queue)
        if length < 1:
          break

        index = _randrange(0, length)
        link = self.visit_queue.pop(index)
        self.visit(link)
    else:
      while True:
        length = len(self.visit_queue)
        if length < 1:
          break

        link = self.visit_queue.pop()
        self.visit(link)
