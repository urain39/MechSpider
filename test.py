from mechspider import MechSpider

class MySpider(MechSpider):
  USER_AGENT = 'Mozilla/5.0 (X11; U; Linux X86_64; en-US) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/72.0.3626.105 Safari/537.36'
  HANDLE_ROBOTS = False
  HOME_PAGE = 'https://httpbin.org/get'
  RANDOM_VISIT = True
  RANDOM_WAIT = True
  RANDOM_WAIT_FACTOR = 5
  USE_CHARDET = False
  CHARDET_LINE_LIMIT = 64
  ENABLE_DEBUG = True


VISITED_COUNT = 0
@MySpider.pattern(r'.+?httpbin\.org/get')
def _(spider, soup):
  print(soup.text)
  print(spider._visit_groups)
  group = spider.create_group()
  group.method = group.VISIT_METHOD_OPEN

  global VISITED_COUNT
  if VISITED_COUNT < 3:
    for i in range(0, 3):
      group.append(spider.home_page + '?page=' + str(VISITED_COUNT) + '&index=' + str(i))
  VISITED_COUNT += 1


ms = MySpider()
ms.start()


#print(MySpider.Patterns)
#print(MechSpider.Patterns)
