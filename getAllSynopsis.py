
import os.path
from bs4 import BeautifulSoup
from dbhelper import DBHelper

# append all summaries and titles into a single file

filenameSumm = 'SouthParkEpisodeSummariesALL.txt'
filenameTitle = 'SouthParkEpisodeTitlesALL.txt'
dbname = 'SouthParkEpisodesSummariesDB.sqlite'

db = DBHelper(dbname=dbname)
keys = db.get_keys()

with open(filenameTitle,'w') as f:
  for key in keys:
    f.write(key+' ')
with open(filenameSumm,'w') as f:
  for key in keys:
    f.write(db.get_items(key)[0].replace('\n',' '))