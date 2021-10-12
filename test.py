from mechspider import MechSpider

class MySpider(MechSpider):
  UserAgent = 'Mozilla/5.0 (X11; U; Linux X86_64; en-US) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/72.0.3626.105 Safari/537.36'
  HandleRobots = False
  FirstPage = 'https://baidu.com'
  RandomVisit = True
  DebugMode = True


@MySpider.pattern(r'.+')
def _(soup, spider):
  print(soup.text)


ms = MySpider()
ms.visit_queue.append('https://so.com')
ms.visit_queue.append('https://163.com')
ms.visit_queue.append('https://baidu.com')
ms.start()

#print(MySpider.Patterns)
#print(MechSpider.Patterns)
