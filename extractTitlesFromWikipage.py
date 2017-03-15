
from bs4 import BeautifulSoup

# note: wikipedia page should be crawled first
# because this was just one page, I did not create a separate spider for it
# can be done manually through scrapy, or just download the entire html
# file manually
# used the following url:
# https://en.wikipedia.org/wiki/List_of_South_Park_episodes
# saved it as episodes-wiki.html
# 
# go through the wikipedia page
# and find the titles of the episodes
# then convert them into a format in which they are represented on
# the south park wikia 

filename = 'episodes-wiki.html'
titles = []
content = ''
with open(filename, 'rb') as f:
    content = f.read()
    f.close()

if content != '' or content != None:
  soup = BeautifulSoup(content)
  for table in soup.findAll('table', {'class':'wikiepisodetable'}):
    rows = table.findAll('tr')
    for tr in rows:
        cols = tr.findAll('td')
        if len(cols) >= 4:
          link = cols[1].find('a').get('title')
          link = link.replace('(South Park)','')
          link = link.split(" ")
          link = [l for l in link if l != '']
          link = '_'.join(link)
          titles.append(link)

savefilename = 'titles.txt'
with open(savefilename, 'w') as w:
  for item in titles:
    w.write('{0}\n'.format(item))
  w.close()