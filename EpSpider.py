
import scrapy
from bs4 import BeautifulSoup

# spider for downloading the episode summaries and scripts 
# to crawl the episode summaries, use the line:
#   http://southpark.wikia.com/wiki/{0}
# to crawl the episode scripts, use the line: 
#   http://southpark.wikia.com/wiki/{0}/Script

class EpSpider(scrapy.Spider):
    name = "episodeswiki"
    filename = 'titles.txt'

    def start_requests(self):
        filename = 'titles.txt'
        titles = []
        with open(filename, 'r') as f:
          for line in f:
            titles.append(line.replace('\n','').replace('\'','%27')) 
        urls = [
            'http://southpark.wikia.com/wiki/{0}'.format(t) for t in titles
            #'http://southpark.wikia.com/wiki/{0}/Script'.format(t) for t in titles
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        page = response.url.split("/")[-1]
        filename = 'episodes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
