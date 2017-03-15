
# By Tim Bergman
#
# Text-based Markov Chain Model learner and generator
# for south park chatbot functionality

# ************************ IMPORTS ********************************

import random, re, codecs
import spacy

class TextMarkovChain():

  # ************************ CONSTRUCTOR *****************************

  def __init__(self, 
    depth=3, 
    text = None, textlist = None, filename = None, 
    nlp = None):
    # initializes the markov chain text generator
    # parameters:
    #   - depth: how many words to use to look ahead to predict new words
    #   - text/textlist/filename: 3 ways to give text to make a corpus
    #     any one of them is sufficient. 
    #     - text: one wall of text the words of which will be the corpus
    #     - textlist: a list of all text strings to be used as a corpus
    #     - filename: a file to a textfile from which text will be read
    #   - nlp: spacy natural language processing pipeline (optional)

    self.allwords = []

    if filename is not None: # if we get passed a file, 
      self.getTextFromFile(filename) # get corpus from file

    if textlist is not None: # else if we get a list of texts, 
      self.getTextFromTextList(textlist) # use those to build corpus

    if text is not None: # else if we get a large block of text
      self.allwords += text.split() # split it into words and use that

    if self.allwords == []: # if our corpus is empty,
      return # we can't do anything, so just abandon ship and return

    self.depth = depth # look-ahead depth to predict words with
    
    self.nlp = nlp # spacy natural language processing pipeline

    self.chaintable = {} # dict with predictor word-keys and possible values
    self.generateTable() # generate the prediction matrix

    self.nlpdict = {}
    self.nlptable = {} # dict with predictor nlp tag keys and possible values 
    self.allnlpwords = []
    self.generateNLPData() # generate the nlp table

  # ************************ INPUT PROCESSING *****************************

  def getTextFromTextList(self, textlist):
    # fetches all the text lines in the list of texts
    # splits them up into individual words 
    # and adds them to our list of allwords-dataset

    for text in textlist:
      self.allwords += text.split()

  def getTextFromFile(self, filename):
    # fetches all the text from a file, 
    # splits them up into individual words 
    # and adds them to our list of allwords-dataset

    with codecs.open(filename,'r',encoding='utf-8',errors='ignore') as f:
      self.allwords += f.read().split()

  # ******************* MARKOV CHAIN GENERATION ************************

  def getTuple(self, drawfrom):
    # get a tuple of length specified in our depth field
    # pulls the tuple sequentially from drawfrom until there are no more
    # this means drawfrom must be one of our allwords lists
    # in our case: allwords, or allnlpwords

    if len(drawfrom) < self.depth:
      return

    for i in range(0,len(drawfrom) - self.depth):
      yield [drawfrom[i+d] for d in range(0,self.depth)]

  def generateTable(self):
    # for each tuple with length l as specified in our depth field,
    # use the first l-1 elements as a prediction-key
    # and use the last element as the predicted value

    for tup in self.getTuple(self.allwords):
      val = tup[-1]
      key = str(tup[0:-1])
      if key in self.chaintable:
        self.chaintable[key].append(val)
      else:
        self.chaintable[key] = [val]

  def generateNLPData(self):
    # sets up the nlp data that we can use to generate text
    # if our natural language pipeline processor is not None, we can setup
    # first, it will process natural language analyses on all given words
    # then, for all tags we have, we will create a list of possible words
    # then, we setup our nlptable on nlp TAGS rather than the words
    # this way, we can create sentences based on nlp tags
    # and then drawing words to fill the nlp tags

    if self.nlp is not None:
      self.allnlpwords = self.nlp(' '.join(self.allwords))
      
      for word in self.allnlpwords:
        if not word.tag in self.nlpdict:
          self.nlpdict[word.tag] = []
        self.nlpdict[word.tag].append(word.text)

      for tup in self.getTuple(self.allnlpwords):
        val = tup[-1]
        key = tup[0:-1]
        tagkey = str([k.tag for k in key])
        if tagkey in self.chaintable:
          self.nlptable[tagkey].append(val.tag)
        else:
          self.nlptable[tagkey] = [val.tag]

  # ************************ TEXT GENERATION *****************************

  def generateText(self, 
    textlength = 30, 
    fullsentences = True, 
    usenlp = False):
    # if usenlp is set to True, use nlp pos tags to generate text
    # else, just use the words-based markov chain 

    if not usenlp:
      return self.generateTextStd(textlength, fullsentences)
    else:
      return self.generateTextNLP(textlength, fullsentences)

  def generateTextNLP(self, textlength = 30, fullsentences = True):
    # this will generate text working from POS tags rather than words
    # first creating a markov chain of pos tags
    # then filling those pos tags with a word from our word dict
    # N.B.: not entirely sure if this gives us a much different
    # behaviour than just going with the standard text-based markov 
    # text generation method. this was a bit of an experiment to see
    # if it worked... it kind of does. I'm just not sure how much better
    # if at all.
    #
    # choose a random index to use as the first word-tag
    # then, use the depth-1 words starting from that index as a predictor
    # get a random predicted value from our nlptable
    # then, 'forget' the first tag of the predictor seed
    # and store the new-predicted value into the new predictor seed set
    # repeat until we are at the word length of (textlength)
    # then, if fullsentences is set to True,
    # remove half-sentences at the beginning and end of the generated text

    firstwordindex = random.randint(0, len(self.allnlpwords)-self.depth-1)
    seeds = [self.allnlpwords[firstwordindex + c] 
      for c in range(0,self.depth-1)]
    seeds = [s.tag for s in seeds]
    tags = []
    text = []
    for i in range(textlength-self.depth-1):
      #print(i,seeds)
      tags.append(seeds[0])
      seeds = []+seeds[1:]+[random.choice(self.chaintable[str(seeds)].tag)]
    tags = tags + seeds[1:]
    for tag in tags:
      text = text + [random.choice(self.nlpdict[tag])]
    text = ' '.join(text)
    if fullsentences:
      text = self.stripToFullSentences(text)
    return text

  def generateTextStd(self, textlength = 30, fullsentences = True, seed = None):
    # choose a random index to use as the first word
    # then, use the depth-1 words starting from that index as a predictor
    # get a random predicted value from our wordchaintable
    # then, 'forget' the first word of the predictor seed
    # and store the new-predicted value into the new predictor seed set
    # repeat until we are at the word length of (textlength)
    # then, if fullsentences is set to True,
    # remove half-sentences at the beginning and end of the generated text

    firstwordindex = random.randint(0, len(self.allwords)-self.depth-1)
    firstwordindex = firstwordindex if seed == None else seed
    seeds = [self.allwords[firstwordindex + c] for c in range(0,self.depth-1)]
    text = []
    for i in range(textlength-self.depth-1):
      #print(i,seeds)
      text.append(seeds[0])
      seeds = [] + seeds[1:] + [
      random.choice(self.chaintable[str(seeds)]) if str(seeds) in self.chaintable 
      else ''
      ]
    text = text + seeds[1:]
    text = ' '.join(text)
    if fullsentences:
      text = self.stripToFullSentences(text)
    return text

  def Cartmanify(self, giventext, textlength = 30, fullsentences = True,
    useTopN = 2):
    # given a text giventext, will adjust the text by nlp tags
    # and similarity to find 'synonyms' as used by the character
    # this will (hopefully) give more 'personality' to the answer
    # textlength will prune the sentence to the given length
    # fullsentences, if True, will snip incomplete sentences from the 
    # front and back of the returned text
    # useTopN will only use the top N words as found in the similarity 
    # search for synonym detection (else you can get weird sentences)

    if self.nlp is None:
      return giventext
    else:
      text = []
      doc = self.nlp(giventext)
      for d in doc:
        tag = d.tag
        if tag in self.nlpdict:
          mostsimilar = [str(d)]
          mostsimilarval = 0
          for n in self.nlpdict[tag]:
            sim = d.similarity(self.nlp(n))
            if sim > mostsimilarval:
              mostsimilarval = sim
              mostsimilar.append(str(n))
          mostsimilar = list(reversed(mostsimilar))[:useTopN]
          text.append(mostsimilar[random.randrange(0,len(mostsimilar))])
        else:
          text.append(str(d))
      text = ' '.join(text)
      if fullsentences:
        text = self.stripToFullSentences(text)
      return text

  def stripToFullSentences(self, text):
    # removes half-sentences at the beginning and end of the generated text

    p = list(re.finditer('[\.\!\?]',text))
    if len(p) > 0:
      m = p[0].start()+1
      text = text[m:]
    if len(p) > 1:
      text = text[:p[-1].start()-m+1]
    return text
