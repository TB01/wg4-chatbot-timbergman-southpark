
import os.path
from bs4 import BeautifulSoup
from dbhelper import DBHelper
import unicodedata

# from a downloaded web page of an episode's information
# go through the file and extract the summary information
# then append it to the database

filename = 'titlesPROC.txt'
dbname = 'SouthParkEpisodesSummariesDB.sqlite'
writeToDB = True # false for testing, true for actual writing to DB

def remove_text_inside_brackets(text, brackets="()[]"):
    count = [0] * (len(brackets) // 2) # count open/close brackets
    saved_chars = []
    for character in text:
        for i, b in enumerate(brackets):
            if character == b: # found bracket
                kind, is_close = divmod(i, 2)
                count[kind] += (-1)**is_close # `+1`: open, `-1`: close
                if count[kind] < 0: # unbalanced bracket
                    count[kind] = 0
                break
        else: # character is not a bracket
            if not any(count): # outside brackets
                saved_chars.append(character)
    return ''.join(saved_chars)

if writeToDB:
  db = DBHelper(dbname=dbname)
  db.setup()

titles = []
with open(filename, 'r') as f:
  for line in f:
    titles.append('./episodes_summaries/{0}'.format(line.replace('\n',''))) 

s = 0

l = len(titles)
dbprelim = {}

def add_to_dict(dic, key, val):
  if key not in dic:
    dic[key] = []
  dic[key].append(val)

for ti in range(s,l):
  t = titles[ti]
  print(ti,t)
  if os.path.isfile(t):
    print('processing: {0}'.format(t))
    with open(t, encoding='utf8') as f:
      fstr = f.read()
      soup = BeautifulSoup(fstr, 'html.parser')
      th = soup.find('h1') # owner, title
      synh = soup.find(text='Synopsis') # synopsis section
      if synh is not None: td = synh.findNext('p')
      if th is not None and td is not None:
        owner = th.get_text()
        if owner is not u'':
          descr = td.get_text().replace('\n','').strip()
          #print(owner, descr)
          add_to_dict(dbprelim, owner, descr)

print([k for k in dbprelim])

if writeToDB:
  for owner in dbprelim:
    if owner is not u'':
      print('working on summary of {0}'.format(owner))
      for descr in dbprelim[owner]:
        try:
          db.add_item(descr,owner)
        except Exception as e:
          print(e)
          pass

  for owner in dbprelim:
    print('summary of {0}'.format(owner))
    descr = db.get_items(owner)
    print(descr)