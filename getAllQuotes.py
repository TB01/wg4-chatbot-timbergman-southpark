
import os.path
from bs4 import BeautifulSoup
from dbhelper import DBHelper

# append all quotes into a single file

filename = 'SouthParkEpisodeQuotesALL.txt'
dbname = 'SouthParkEpisodesDB.sqlite'

db = DBHelper(dbname=dbname)
keys = db.get_keys()

with open(filename,'w',encoding='utf-8') as f:
  for key in keys:
    for item in db.get_items(key):
      print(key, item)
      f.write(item.replace('\n',' '))