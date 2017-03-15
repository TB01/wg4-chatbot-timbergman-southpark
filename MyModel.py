
# by Tim Bergman
#
# TODO:
# - fix Cartmanify function. i.e.: 
#     - better synonym detection for substituting words 
#       in a text with the markov-chain text model based on
#       a corpus of a character's quotes 
#       this way, we could 'personify' some given text to make it 
#       sound like a character
#     - insert filler words, phrases, etc. in a similar way to personify
# - make it actually chatty (i.e. make it coherent)
# - fix the similarity measure that measures how similar a user's
#   input is to the key phrases or commands that will trigger
#   a certain query behaviour (for example: 'give an episode synopsis'
#   or 'say the following like butters: i like bananas or whatever'
#
# uses assets from:
#     http://southpark.wikia.com/wiki/South_Park_Archives
#
# South Park copyright info: 
#     http://southpark.cc.com/about/legal/terms-of-use
#
# for education purposes only

# ************************ IMPORTS ********************************

from Model import Model
from dbhelper import DBHelper
import random
import spacy
import numpy as np
from nltk.sentiment.vader import SentimentIntensityAnalyzer
# Hutto, C.J. & Gilbert, E.E. (2014). 
# VADER: A Parsimonious Rule-based Model for Sentiment Analysis of Social Media Text. 
# Eighth International Conference on Weblogs and Social Media (ICWSM-14). 
# Ann Arbor, MI, June 2014
from TextMarkovChain import TextMarkovChain

# ******************** CHATBOT MODEL CLASS ************************

class MyModel(Model):
  # model which can respond to queries with south park material
  # don't forget to specify parameters in the constructor
  # usage: pars = <your parameter dictionary here>
  # fields in parameter dict used in this model: 
  # qdbname: name/path to sqlite database file with quotes per character
  # sdbname: name/path to sqlite database file with summary per episode
  # mtitlename: name/path to txt file holding ALL available episode titles
  # msumname: name/path to txt file holding ALL available episode synopses
  # mquotename: name/path to txt file holding ALL available quotes
  # usenlpformarkov: if True, use nlp pos tags for markov text generation
  # cartmanify: if True, will use markov chain to 'personify' answers
  # debug: if True, will output debug messages

  # ************************ CONSTRUCTOR ********************************

  def __init__(self, *args, **kwargs):
    # initializes the model

    print('Initializing model...')

    # constructor of super-class. Stores parameters if given in kwargs
    # pass them as argument as: pars = <your parameter dictionary here>
    Model.__init__(self, *args, **kwargs)

    # get database names as given in the parameters or default them
    qdbname = 'SouthParkEpisodesDB.sqlite' if 'qdbname' not in self.pars else self.pars['qdbname']
    sdbname = 'SouthParkEpisodesSummariesDB.sqlite' if 'sdbname' not in self.pars else self.pars['sdbname']
    msumname = 'SouthParkEpisodeSummariesALL.txt' if 'msumname' not in self.pars else self.pars['msumname']
    mtitlename = 'SouthParkEpisodeTitlesALL.txt' if 'mtitlename' not in self.pars else self.pars['mtitlename']
    mquotename = 'SouthParkEpisodeQuotesALL.txt' if 'mquotename' not in self.pars else self.pars['mquotename']
    
    # load and setup the quotes and episode summary databases
    self.qdb = DBHelper(dbname=qdbname) # quotes database
    self.qdb.setup()
    self.sdb = DBHelper(dbname=sdbname) # episode synopsis database
    self.sdb.setup()
    
    # initialize the markov chain text generators
    self.mtitle = TextMarkovChain(filename = mtitlename, depth = 2)
    self.msum = TextMarkovChain(filename = msumname, depth = 2)
    self.mquote = TextMarkovChain(filename = mquotename, depth = 2)
    self.mchar = {} # holds markovchainmodels per requested character
    
    # get all characters and episodes we have data of
    self.chars = self.qdb.get_keys() # which characters do we have quotes from
    self.episodes = self.sdb.get_keys() # which episode titles do we have?
    
    # initialize spacy's natural language processing pipeline for english
    self.nlp = spacy.load('en')
    # do we want to use nlp pos tags for markov chain text generation?
    self.usenlpformarkov = False if 'usenlpformarkov' not in self.pars else self.pars['usenlpformarkov']
    self.cartmanify = False if 'cartmanify' not in self.pars else self.pars['cartmanify']
    
    # if set to true, will give debug messages
    self.debug = self.pars['debug'] if 'debug' in self.pars else False
    
    self.currentChar = {} # character currently active with each chat partner
    self.partnerInfo = {} # dict to store info on chat partners
    self.sent = SentimentIntensityAnalyzer() # VADER sentiment analyzer
    
    # the queries/response functions that we specify can be made
    self.queries = [
      self.SetCharacterQuery, # did the user request a change in character?
      self.SynopsisQuery, # outputs the synopsis of an episode
      self.GenerateSynopsisQuery, # generates a new synopsis from model
      self.GenerateQuoteQuery, # generates a new quote from model
      self.GenerateQuoteAsCharQuery, # generates a new quote from char model
      self.GoodbyeQuery, # did the user say goodbye?
      self.CartmanifyQuery, # did the user want char to say something?
      self.GreetingsQuery, # did user introduce/greet the bot?
      self.InfoQuery, # did user request information on the bot?
      self.IdleQuery, # if all other query-types return false, do this.
    ]
    self.queryphrases = {
      'setchar':['setchar', 'can i speak to', 'can i talk to',
        'i want to speak to','i want to talk to',
        'give me'],
      'sayhi':['sayhi', 'hello', 'hi ', 'bonjour', 'guten tag', 'konnichiwa'],
      'saybye':['saybye','goodbye','bye', 'farewell', 'fare thee well'],
      'givesyn':['givesyn','give a synopsis','give a summary',
        'give me a synopsis','give me a summary'],
      'createsyn':['createsyn','generate a synopsis', 'create a synopsis',
        'create a summary','generate a synopsis'],
      'createquot':['createquot','generate a quote','create a quote'],
      'sayaschar':['sayaschar','say something like','speak like',
        'talk like'],
      'setname':['setname','my name is','i am'],
      '/info':['/help','/info'],
      'cartmanify':['cartmanify'],
    }
    
    print('\tModel initialization done!')

  # ************************ RESPOND FUNCTION ***************************

  def respond(self, text, chat):
    # create spacy natural language pipeline analysis of text
    # then go through all queries that we specified can be made
    # see if it was said query, and if so, output back the response

    doc = self.nlp(text)

    for query in self.queries:
      (isQuery,response) = query(doc, chat)
      if isQuery:
        break

    return (response, chat, None)

  # ************************ QUERY CHECKER ****************************

  def CheckQuery(self, doc, command, keyphrases=[], simthresh = 0.75):
    # checks if the nlprocessed text of the user (doc) has any commands
    # or keyphrases in them, in which case return True, as in:
    # the input text has in it the query which we can do something with.
    #
    # TODO: implement similarity to keyphrases such that they are 
    # robust. If certainty of this similarity to the keyphrases is
    # greater than the similarity-threshold, then return True as well

    if command in [str(d).lower() for d in doc]:
      return True

    if len(keyphrases) >= 1:
      
      for key in keyphrases:
        if key in str(doc):
          self.DebugLog('CheckQuery TRUE for: {0}, {1}, {2}'.format(
            command, key, str(doc)))
          return True

      certainty = 0
      # calculate certainty that input sentence is similar enough
      # to keyphrases
      # NOT YET IMPLEMENTED.
      if certainty >= simthresh:
        return True

    return False

  # ************************ QUERY HANDLERS ****************************

  def InfoQuery(self, doc, chat):
    # Checks if user has entered a query to get information on the bot
    # if so, return information on the bot, what commands and phrases
    # can be used, etc.

    if self.CheckQuery(doc, '/info', self.queryphrases['/info']):
      return (True, self.infostring())
    return (False, str(doc))

  def SetCharacterQuery(self, doc, chat):
    # Checks if the user has entered a query to set/change the character
    # if so, set the current character of this chat
    # and return a response of the character

    if self.CheckQuery(doc, 'setchar', self.queryphrases['setchar']):
      for d in doc:
        for c in range(0,len(self.chars)):
          if str(d).lower() == self.chars[c].lower():
            self.SetCurrentChar(chat,c)
            return (True, self.GetCharacterResponse(doc,chat))

    return (False, str(doc))

  def GenerateQuoteAsCharQuery(self, doc, chat):
    # Checks if the user has entered a query to request a character quote
    # if so, set the current character of this chat
    # and return a response of the character
    # this will actually generate a markov-text response rather than a
    # quote of the character from the scripts

    if self.CheckQuery(doc, 'sayaschar', self.queryphrases['sayaschar']):
      for d in doc:
        for c in range(0,len(self.chars)):
          if str(d).lower() == self.chars[c].lower():
            self.SetCurrentChar(chat,c)
            return (True, self.SaySomethingLike(doc, chat))
    return (False, str(doc))

  def GreetingsQuery(self, doc, chat):
    # Checks if the user has entered a query to request a greeting
    # if so, greet the chat partner.
    # if, in addition, the chat partner has entered a query to set
    # their name info field, set that as well
    # will append the name info field to the greeting as well, if
    # we have the name info
    # also, if we have set cartmanify to True, it will try to
    # create a response based on the markov chain model and nlp tag
    # similarity to 'personalize' the response like the character
    # that this chat session has been set to

    if self.CheckQuery(doc, 'setname', self.queryphrases['setname']):
      value = str(doc[1])
      self.SetPartnerInfo(chat, 'name', value)
      text = 'Hello {0}!'.format(self.GetPartnerInfo(chat,'name'))
      if self.cartmanify:
        text = self.Cartmanify(text, chat)
      return (True, text)
    if self.CheckQuery(doc, 'sayhi', self.queryphrases['sayhi']):
      text = 'Hello {0}!'.format(self.GetPartnerInfo(chat,'name'))
      if self.cartmanify:
        text = self.Cartmanify(text, chat)
      return (True,text)
    return (False, str(doc))

  def GoodbyeQuery(self, doc, chat):
    # Checks if the user has entered a query to request a farewell
    # if so, say goodbye to the chat partner.
    # will append the name info field to the greeting as well, if
    # we have the name info
    # also, if we have set cartmanify to True, it will try to
    # create a response based on the markov chain model and nlp tag
    # similarity to 'personalize' the response like the character
    # that this chat session has been set to

    if self.CheckQuery(doc, 'saybye', self.queryphrases['saybye']):
      text = 'Goodbye {0}!'.format(self.GetPartnerInfo(chat,'name'))
      if self.cartmanify:
        text = self.Cartmanify(text, chat)
      return (True, text)
    return (False, str(doc))

  def CartmanifyQuery(self, doc, chat):
    # Checks if the user has entered a query to request a cartmanification
    # if so, cartmanify the rest of the chat partner's input query.
    # this is mostly for testing the cartmanify function

    if self.CheckQuery(doc, 'cartmanify', self.queryphrases['cartmanify']):
      print(str(doc))
      text = str(doc).replace('cartmanify','')
      print(text)
      for phrase in self.queryphrases['cartmanify']:
        text = text.replace(phrase,'')
        print(text)
      if self.cartmanify:
        text = self.Cartmanify(text, chat)
      return (True, text)
    return (False, str(doc))

  def SynopsisQuery(self, doc, chat):
    # Checks if the user has entered a query to request a synopsis
    # if so, get a random synopsis from the episodes
    # and return it

    if self.CheckQuery(doc, 'givesyn', self.queryphrases['givesyn']):
      titles = self.episodes
      r = random.randrange(0,len(titles))
      title = titles[r]
      item = self.sdb.get_items(title)[0]
      self.DebugLog(title,item,chat=chat)
      return (True, 'Summary for '+title+'\n\n'+item)
    return (False, str(doc))

  def GenerateSynopsisQuery(self, doc, chat):
    # Checks if the user has entered a query to request a
    # markov-generated synopsis
    # if so, get a markov-text generated synopsis
    # and return it

    if self.CheckQuery(doc, 'createsyn', self.queryphrases['createsyn']):
      return (True, 'Summary for ' + 
        self.mtitle.generateText(15) + 
        '\n\n' + 
        self.msum.generateText(150))
    return (False, str(doc))

  def GenerateQuoteQuery(self, doc, chat):
    # Checks if the user has entered a query to request a
    # markov-generated quote (non-character specific)
    # if so, get a markov-text generated synopsis
    # and return it

    if self.CheckQuery(doc, 'createquot', self.queryphrases['createquot']):
      return (True, self.mquote.generateText(50))
    return (False, str(doc))

  def IdleQuery(self, doc, chat):
    # if all other queries fail, just return an idle response.
    # if a character has been set, this will be a random quote
    # if not, it will just echo back the user input

    if chat in self.currentChar:
      return (True, self.GetCharacterResponse(doc,chat)) 
    return (True, str(doc)) # just echo when all else fails

  # ******************* GETTERS AND SETTERS ***************************

  def SetCurrentChar(self, chat, char_index):
    # sets the current chat's active character to the one given

    self.currentChar[chat] = char_index

  def GetPartnerInfo(self, chat, key):
    # gets info on the chat partner as given by their chat-id
    # and the key (for example: name)
    # for example: self.GetPartnerInfo(2256,'name') might return 'Bob'

    if chat not in self.partnerInfo:
      self.SetPartnerInfo(chat, key, '')
    return self.partnerInfo[chat][key]

  def SetPartnerInfo(self, chat, key, value):
    # this will set info on the chat partner as given by their chat-id
    # and the key (for example: name), to the value
    # for example: self.SetPartnerInfo(2256,'name','Bob') 
    # will set the name info field of chat partner 2256 to 'Bob'

    if chat not in self.partnerInfo:
      self.partnerInfo[chat] = {}
    self.partnerInfo[chat][key] = value

  def Cartmanify(self, text, chat):
    # NOTE: THIS DOES NOT WORK VERY WELL
    # 
    # This function will get some generated text to be output
    # and will try to personify it with the currently active character
    # by substituting words in the given tags with
    # words that the character uses a lot as given in the markov model
    # on the basis of which nlp-tags they are, and similarity
    #
    # TODO: make this work better
    # ideas: 
    #   - better synonym detection?
    #   - incorporate filler words that characters often use?

    self.DebugLog('Cartmanify',chat=chat)
    currentChar = -1
    if chat in self.currentChar:
      currentChar = self.currentChar[chat]
    if currentChar != -1:
      char = self.chars[currentChar]
      if char in self.mchar:
        text = self.mchar[char].Cartmanify(text, 50, True)
      else:
        self.mchar[char] = TextMarkovChain(depth=2,
          textlist=self.qdb.get_items(char), nlp=self.nlp)
        text = self.mchar[char].Cartmanify(text, 50, True)
      return '{0}: {1}'.format(char,text)
    return text

  def GetCharacterResponse(self, doc, chat):
    # this will return some random character response
    # 
    # TODO: make this more 'chatty'
    # ideas: 
    #   - currently experimenting with: 
    #       - generating standard chat responses
    #       - then 'cartmanifying' it with the character's markov chain
    #   - alternatively, go through quotes database and pick
    #     a quote to respond with on the basis of similarity to
    #     a 'normal' chat answer 

    self.DebugLog('sentiment: {0}'.format(
      self.sent.polarity_scores(str(doc))),
      chat=chat)
    char_index = self.currentChar[chat]
    char = self.chars[char_index]
    dbitems = self.qdb.get_items(char)
    item = dbitems[random.randrange(0,len(dbitems))]
    return '{0}: {1}'.format(char,item)

  def SaySomethingLike(self, doc, chat):
    # this will return a response text that will be based on the
    # markov text chain model as trained on the character's
    # quotes from the scripts as a corpus
    # as such, it will return a text that SOUNDS like a character
    # BUT! this does not return anything meaningful.
    #
    # TODO:
    #   - make this more chatty. i.e. make it more coherent
    #     as currently, it only spits out random markov text
    #     and ideally, we would want it to actually say something

    self.DebugLog('say something like called',chat=chat)
    currentChar = -1
    text = ''
    if chat in self.currentChar:
      currentChar = self.currentChar[chat]
    if currentChar != -1:
      char = self.chars[currentChar]
      if char in self.mchar:
        text = self.mchar[char].generateText(50, True,
          self.usenlpformarkov)
      else:
        self.mchar[char] = TextMarkovChain(depth=2,
          textlist=self.qdb.get_items(char), nlp=self.nlp)
        text = self.mchar[char].generateText(50, True,
          self.usenlpformarkov)
    return '{0}: {1}'.format(char,text)

  # ************************ MISC FUNCTIONS *****************************

  def DebugLog(self, *debugtext, chat=''):
    # displays debug messages if we have set debug mode to True
    # if chat parameter is specified, it will specify which chat
    # the message belongs to. 
    # use to pass argument: chat = <chat integer id here>
    # can send any number of debug messages. pass before chat-statement

    if self.debug: 
      print('debug: {0}: ({1})'.format(
        str(chat),','.join([str(d) for d in debugtext])))

  def build_keyboard(self, items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)

  def infostring(self):
    # return a string with info on this bot

    greetings = 'Hello! I am SouthParkBot!'
    
    generalinfo = 'I output not only episode summaries or quotes \
      from the characters in the show, \
      but can also be trained to output newly generated summaries \
      and quotes in the style of South Park and its characters.'
    
    commands = 'Specifically, I can exhibit the following behaviours: \
    \n\
    setchar: Sets the current character to the requested character and outputs a quote from them.\
    Alternative phrases you can use:\
    i want to speak to <character name>,\
    i want to talk to <character name>,\
    give me <character name\
    \n\
    sayhi:\
    Will introduce the chatbot and output a greeting.\
    If the person\'s name is known, it will also greet the person using the the stored chat partner information name field.\
    Alternative phrases you can use:\
    hello,\
    hi,\
    bonjour,\
    guten tag,\
    konnichiwa\
    \n\
    saybye:\
    Will say goodbye. If the person\'s name is known, it will also greet the person using the stored chat partner information name field.\
    Alternative phrases you can use: \
      goodbye,\
      bye,\
      farewell,\
      fare thee well\
    \n\
    givesyn:\
      Will output a synopsis of an existing episode.\
      Alternative phrases you can use:\
        give a synopsis,\
        give a summary,\
        give me a synopsis,\
        give me a summary\
    \n\
    createsyn:\
      Creates a new episode synopsis using markov chain text generation. Will not make sense, but will at least sound like a south park episode, I guess...\
      Alternative phrases you can use:\
        generate a synopsis,\
        create a synopsis,\
        create a summary,\
        generate a synopsis\
    \n\
    createquot:\
      Creates some random quote using markov chain text generation. Again, will not make any sense, but it will sound like south park.\
      Alternative phrases you can use:\
        generate a quote\
        create a quote\
    \n\
    sayaschar <character name>:\
      Creates a quote using markov chain text generation drawing from the speech patterns of particular characters. As such, the quotes will at least sound like they have the personality of the requested character, even if they don\'t make any sense in terms of meaning.\
      Alternative phrases you can use:\
        say something like <character name>,\
        speak like <character name>,\
        talk like <character name>\
      \nExample: \
        say something like cartman,\
        speak like tweek,\
        sayaschar satan\
    \n\
    setname <your name>:\
      Creates an information field in the chat partner information database with a \'name\' key. As such, when it needs to use your name (for example in greeting you), it will be able to do so.\
      Alternative phrases you can use:\
        my name is <your name>,\
        i am <your name>,\
      \nExample:\
        my name is john,\
        setname bobina\
    '

    return '{0}\n\n{1}\n\n{2}'.format(greetings, generalinfo, commands)