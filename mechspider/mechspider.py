import re as _re
from bs4 import BeautifulSoup as _Soup
from chardet.universaldetector import UniversalDetector as _UniversalDetector
from mechanize import Browser as _Browser
from random import randrange as _randrange
from .exceptions import PropertyMissingError as _PropertyMissingError


_CharsetDetector = _UniversalDetector()


# pylint: disable=invalid-name
def Soup(*args, **kwargs):
  return _Soup(*args, features='html5lib', **kwargs)


class MechSpider:
  def __init__(self):
    self.visit_queue = []
    self.browser = _Browser()
    self.browser.set_handle_equiv(True)
    self.browser.set_handle_gzip(True)
    self.browser.set_handle_redirect(True)
    self.browser.set_handle_referer(True)
    if hasattr(self, 'UserAgent'):
      self.browser.set_header('User-Agent', self.UserAgent)
    if hasattr(self, 'HandleRobots'):
      self.browser.set_handle_robots(self.HandleRobots)

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
  def _detect_encoding(response, max_line_count=128):
    response.seek(0, whence=0)
    _CharsetDetector.reset()

    line_count = 1
    while line_count <= max_line_count:
      _CharsetDetector.feed(response.readline())
      if _CharsetDetector.done:
        break
      line_count += 1
    _CharsetDetector.close()
    return _CharsetDetector.result['encoding']

  def _visit(self, url):
    # pylint: disable=consider-using-dict-items
    for pattern in self.Patterns:
      if pattern.match(url) is not None:
        #print(url + ' wanted by ' + str(pattern))
        callback = self.Patterns[pattern]
        # pylint: disable=assignment-from-none
        response = self.browser.open(url) # WTF? x2
        encoding = self._detect_encoding(response)
        markup = response.get_data().decode(encoding)
        soup = Soup(markup=markup)
        callback(soup, self)
        break

  def start(self):
    if hasattr(self, 'HomePage'):
      self.browser.open(self.HomePage)
    else:
      raise _PropertyMissingError('HomePage missing')

    random_visit = self.RandomVist \
      if hasattr(self, 'RandomVist') else False

    if random_visit:
      while True:
        length = len(self.visit_queue)
        if length < 1:
          break

        index = _randrange(0, length)
        url = self.visit_queue.pop(index)
        self._visit(url)
    else:
      while True:
        length = len(self.visit_queue)
        if length < 1:
          break

        url = self.visit_queue.pop()
        self._visit(url)
