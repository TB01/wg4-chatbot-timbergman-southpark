
import os.path
from bs4 import BeautifulSoup
from dbhelper import DBHelper
import unicodedata

# from a downloaded web page of the south park wikia containing a script
# go through the file and append a character's line to the quote
# database entry belonging to that character

filename = 'titlesPROC.txt'
dbname = 'SouthParkEpisodesDB.sqlite'
writeToDB = False # false for testing, true for actual writing to DB

def remove_text_inside_brackets(text, brackets="()[]"):
  # stole this from stackoverflow
  # answer of user J.F. Sebastian on Jan 30 '13 at 12:01
  # http://stackoverflow.com/questions/14596884/remove-text-between-and-in-python

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
    titles.append('./episodes_scripts/{0}'.format(line.replace('\n',''))) 

s = 0
s = 31

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
    with open(t,'r') as f:
      fstr = f.read()
      try:
        unicode(fstr, "ascii")
      except UnicodeError:
        fstr = unicodedata.normalize('NFKD', fstr.decode('utf8'))
        fstr = u''.join(c for c in fstr if not unicodedata.combining(c))
      soup = BeautifulSoup(fstr, 'html.parser')
      for table in soup.findAll('table', {'class':'wikitable'}): 
        for tr in table.findAll('tr'):
          th = tr.find('th')
          td = tr.find('td')
          if th is not None and td is not None:
            owner = th.get_text().replace(':','').strip()
            if owner is not u'':
              descr = remove_text_inside_brackets(td.get_text()).replace('\n','').strip()
              #print(owner, descr)
              add_to_dict(dbprelim, owner, descr)

print([k for k in dbprelim])

if writeToDB:
  for owner in dbprelim:
    if owner is not u'':
      print('working on quotes from {0}'.format(owner))
      for descr in dbprelim[owner]:
        try:
          db.add_item(descr,owner)
        except Exception as e:
          print(e)
          pass

  for owner in dbprelim:
    print('quotes from {0}'.format(owner))
    descr = db.get_items(owner)
    print(descr)