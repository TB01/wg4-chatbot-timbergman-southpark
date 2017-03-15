
class Model():
  # base class for chatbot-model
  # holds the only two functions every child-class of model needs
  #
  # __init__ (base init will store parameter dict, if any)
  # pass parameters as: pars=<your parameter dict here>
  #
  # respond(self, text, chat) which should be overloaded in child classes
  # and will respond to the given text as given in chat given by chat id

  # ************************ CONSTRUCTOR ********************************

  def __init__(self, *args, **kwargs):
    # base constructor
    # stores parameter dictionary if any
    
    self.pars = kwargs['pars'] if 'pars' in kwargs else {}

  # ************************ RESPOND FUNCTION ****************************

  def respond(self, text, chat):
    # base respond method. overload in child classes!
    
    return ('', chat, None)