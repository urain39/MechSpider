from mechspider import MechSpider

class MySpider(MechSpider):
  USER_AGENT = 'Mozilla/5.0 (X11; U; Linux X86_64; en-US) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/72.0.3626.105 Safari/537.36'
  HANDLE_ROBOTS = False
  HOME_PAGE = 'https://httpbin.org/get'
  MAX_VISIT_COUNT = 64
  RANDOM_VISIT = True
  RANDOM_WAIT = True
  RANDOM_WAIT_FACTOR = 5


@MySpider.pattern(r'.+?httpbin\.org/get')
def _(soup, spider):
  print(soup.text)


ms = MySpider()
ms.start()

#print(MySpider.Patterns)
#print(MechSpider.Patterns)
