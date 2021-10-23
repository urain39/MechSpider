import os
import time
from mechspider import MechSpider


class MySpider(MechSpider):
  USER_AGENT = 'Mozilla/5.0 (X11; U; Linux X86_64; en-US) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/72.0.3626.105 Safari/537.36'
  HANDLE_ROBOTS = False
  HOME_PAGE = 'https://a7a7.net/meitu/index.php/category/fzly/'
  RANDOM_VISIT = True
  RANDOM_WAIT = True
  RANDOM_WAIT_FACTOR = 160
  USE_CHARDET = False
  CHARDET_LINE_LIMIT = 64
  ENABLE_DEBUG = True


ms = MySpider()


@ms.pattern(r'^https://a7a7\.net/meitu/index\.php/category/fzly/$')
def _(spider, soup):
  group = spider.create_group(standalone=True)
  for i in range(1, 19):
    group.append('https://a7a7.net/meitu/index.php/category/fzly/' + str(i) + '/')

@ms.pattern(r'^https://a7a7\.net/meitu/index\.php/category/fzly/\d+/$')
def _(spider, soup):
  group = spider.create_group()
  for a in soup.select('a.item-link'):
    group.append(a.attrs['href'])

@ms.pattern(r'^https://a7a7\.net/meitu/index\.php/archives/\d+/$')
def _(spider, soup):
  title = soup.select('title')[0].text
  if os.path.isdir(title) is False:
    os.mkdir(title)
  os.chdir(title)

  idx = 0
  for pic in soup.select('img.post-item-img.lazy'):
    fullurl = pic.attrs['data-original']
    if fullurl.startswith('//'):
      fullurl = 'https:' + fullurl
    filename = ('%03d' % idx) + '.' + fullurl.split('.')[-1]
    if os.path.isfile(filename) is False:
      print(str(idx) + ' ' + time.strftime("%Y-%m-%d %H:%M:%S"))
      spider.browser.retrieve(fullurl, filename)
    idx += 1

  os.chdir('..')

ms.start()
