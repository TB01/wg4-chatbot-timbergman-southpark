
## ****** THE GENERAL IDEA ******* ##

The idea was to create a chatbot based on South Park episodes and scripts.

Specifically, I wanted to make a chatbot that would get the South Park episode summary and scripts as input info, and could output not only these episodes or quotes from the characters in the show, but could also be trained to output newly generated summaries and quotes in the style of South Park and its characters.

## ****** WHAT IS INSIDE THE REPO? ******* ##

The following files and assorted scripts:
- chatbot - the main file that will run the chatbot itself.
- dbhelper - a database helper class that handles some db operations.
- extractTitlesFromWikipage - given the wikipedia page of the south park episodes list, extract all titles to be used for crawling the south park wikia for summaries and scripts.
- EpSpider - a scrapy crawler to crawl the south park wikia and download the scripts and summaries of the south park episodes as gained by the extractTitlesFromWikipage script.
- processScriptsFromHTML and processSynopsisFromHTML will use the crawled script and summary pages to fetch all script and synopsis data from the HTML and puts them into neatly organized sqlite databases
- getAllQuotes and getAllSynopsis will append all quotes and synopses from an existing quotes and synopsis database into a single file
- Model - base class for chatbot model
- MyModel - the class that will hold the south park chatbot model
- TextMarkovChain - markov chain model specifically made for usage with the south park chatbot. has some experimental features and methods such as 'cartmanify' that are still not functioning as I'd like it to.

## ****** WHAT ELSE IS NEEDED? ****** ##

Requirements:
- python3.x, 64 bit (else spacy will complain)
- BeautifulSoup4, SpaCy, NLTK, Numpy, Scrapy

South Park Episode data:
- databases and files containing episode data (left these out of the repo itself)
- but, these can also be crawled by you via the EpSpider, the 2 process<X>FromHTML and getALL<X> scripts

## ****** WHAT ELSE I WOULD LIKE TO ADD ****** ##

TODO:
- fix Cartmanify function. i.e.: 
    - better synonym detection for substituting words 
      in a text with the markov-chain text model based on
      a corpus of a character's quotes 
      this way, we could 'personify' some given text to make it 
      sound like a character
    - insert filler words, phrases, etc. in a similar way to personify
- make it actually chatty (i.e. make it coherent)
- fix the similarity measure that measures how similar a user's
  input is to the key phrases or commands that will trigger
  a certain query behaviour (for example: 'give an episode synopsis'
  or 'say the following like butters: i like bananas or whatever'

## ****** BEFORE ANYTHING ELSE, ACKNOWLEDGEMENTS, DISCLAIMERS, AND MISCELLANEOUS ASS-COVERING ***** ##

framework of the chatbot and dbhelper is based on:
Gareth Dwyer's tutorial on:
Building a Chatbot using Telegram and Python
https://www.codementor.io/garethdwyer/building-a-telegram-bot-using-python-part-1-goi5fncay
https://github.com/sixhobbits/python-telegram-tutorial

uses assets crawled from http://southpark.wikia.com/wiki/South_Park_Archives

South Park copyright info: http://southpark.cc.com/about/legal/terms-of-use

used a script taken from stackoverflow
namely: the one in the answer of user J.F. Sebastian on Jan 30 '13 at 12:01
at http://stackoverflow.com/questions/14596884/remove-text-between-and-in-python

for education purposes only

## ****** QUERIES, COMMANDS AND KEY PHRASES ****** ##

COMMANDS:

/info
/help 
  Outputs an information or help text that will inform the user on 
  the capabilities of the chatbot and the commands and keyphrases
  that can be used to accomplish certain behaviours.

setchar <character name>
  Sets the current character to the requested character and outputs a quote from them.
  Alternative phrases you can use:
    i want to speak to <character name>
    i want to talk to <character name>
    give me <character name>
  Example:
    setchar butters
    i want to speak to cartman

sayhi
  Will introduce the chatbot and output a greeting.
  If the person's name is known, it will also greet the person using the the stored chat partner information name field. 
  Alternative phrases you can use:
  hello
  hi
  bonjour
  guten tag
  konnichiwa

saybye
  Will say goodbye. If the person's name is known, it will also greet the person using the stored chat partner information name field.
  Alternative phrases you can use: 
    goodbye
    bye
    farewell
    fare thee well

givesyn
  Will output a synopsis of an existing episode.
  Alternative phrases you can use:
    give a synopsis
    give a summary
    give me a synopsis
    give me a summary

createsyn
  Creates a new episode synopsis using markov chain text generation. Will not make sense, but will at least sound like a south park episode, I guess...
  Alternative phrases you can use:
    generate a synopsis
    create a synopsis
    create a summary
    generate a synopsis
      
createquot
  Creates some random quote using markov chain text generation. Again, will not make any sense, but it will sound like south park.
  Alternative phrases you can use:
    generate a quote
    create a quote
  
sayaschar <character name>
  Creates a quote using markov chain text generation drawing from the speech patterns of particular characters. As such, the quotes will at least sound like they have the personality of the requested character, even if they don't make any sense in terms of meaning.
  Alternative phrases you can use:
    say something like <character name>
    speak like <character name>
    talk like <character name>
  Example: 
    say something like cartman
    speak like tweek
    sayaschar satan
      
setname <your name>
  Creates an information field in the chat partner information database with a 'name' key. As such, when it needs to use your name (for example in greeting you), it will be able to do so.
  Alternative phrases you can use:
    my name is <your name>
    i am <your name>
  Example:
    my name is john
    setname bobina

## ****** EXAMPLES ****** ##

generate a synopsis:

Summary for Yourself Mysterion Rises Over Logging Le Petit Tourette An Elephant Makes Love

Mr. Adler, the dangers of getting them and the dangers of Mexico, who has been teasing him from Cartman. Stan Marsh and ignore him, Kenny tries to be evil. Also "Cartman" grows a prank, but no shame in South Park feel they have found their own hands and tired of Cartman's Cupid counterpart tries to make easy money, the townspeople decide to go trick Tweek Tweak has an embarrassing intimate moment in the ultimate sacrifice to fight back.Chef's passionate protest their costumes, at school with one thing could suddenly a circus, and unconscious bias. It is moved to toilet seat up, the American people in school paper. His target is gone. When the time and wreaks havoc on skull island of confessing his friends and deciding that she threatens to build a Thanksgiving special on the campaign rally.

say something like butters

Uh oh. Eric, I'm happy thoouughts! HUT! Oh it's pretty girl! Why can't see them? Oh geez, are you hear me?! What do you ever wants to go and us all right, bitch. Oh, thanks. You know we were coming!

What's a delusion brought on the power of Professor Chaos, and zombies on a live his jokes aren't meant for all messin' with me, I s'psoe Uh, but phonies!

say something like tweek

Oh, Jesus, uh, we have before. I do?! Mine too! Aaaa! I'm in me out of my parents find out! I just... I do?? Well? Nrr. What if they might - you try and I mean, rrrr. Rrrr! I'm not a lucky guy. What?

say something like cartman

Welcome everyone! The Mayans predicted this! Come on! Yeah. Shyeah, that even if you can't just play with poop. What? What'd I do. Yeah, dude, laaame.

Ma'am, the Chinese! Trust me: they're rich, greedy-ass Indians! That's more pure Caucasian dialect. There's gotta go home to do first? Butters, I know that are gonna be a minute. Lucky for full of the other kid. No, we don't give him out of you.

say something like bebe

Stop it all day. I want to Hawaii would you tell anyone this? Why not? Britney Spears got these things run my life. Please, you understand? Water, Helen, Water. Helen, Helen. It puts the best school spirit. Huh, Mandy?

Stupid Spoiled Whore clothes, Stupid Spoiled Whore party. You're invited. Party at everyone's heads. Wow. Wendy and Kyle sittin' in last week.

say something like satan

Enough, Beelzeboot! Thy end has been this party, so we will and I'm just a pussy, Chris, I know the whole area can all over. Halloween is falling, and hook up.

Forget it! Did Diddy had one. Yes it comes. Acura?? But I told you. Saddam, I'm sorry. Chris! But you who make my deal, I love you can stop fighting now!

say something like god

And now you're not being a headstrong rebel. And if you're a whiny little bitch. No, you've become dependent on relationships. So you wish to you? You want to you?

say something like jesus

Good. Want some help! Super Best Friends power of bread and it's still Muhammad and bombs to have you still Muhammad is the prayer of a place called Hell? It's gettin' to school.

say something like towelie

Well, I'm not gettin' me get high? You think you're a ...Towelie ban?... Alright, see ya. Man, I feel like I'm gonna get high, I need to do this?

Stupid... handicapped... camp. That's my God! No-o-o-o! What are so you don't know what you evil towel! Yeah! Awww. Aw man, I really good idea... Yep! And crystal meth. ...aaand crack. Hey wait a really just an extra-special tow- person. Really? Wow.

say something like terrance

?!! But you built an episode that was wrong. Crap. It's the time! Because you've reduced Canada Channel to smut and we didn't come for a rat, buddih! He's not your buddih, friend! Yeah, let's give it up, guy. Well I'm Terrance!

say something like ike

Weee! Weee... Kyle. No-oo. I told you be a ghost. But Daddy I feel like... I'm totally tripping balls. Ice cream. I feel, like me. Shamohn! Hee hee hee. A dainty little kids. She's a ghost. But if I want chocolate. Kyyyle!

say something like chef

Wellll, if you for over now. Just try to Colorado. Your parents turned racist, when I shall perservere. Children, what it about why all of my ass!

