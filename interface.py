import sys, time

from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import TextNode, TransparencyAttrib, Vec3
from direct.task import Task
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText

class Interface(DirectObject):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.dummy = None
    # Function to put instructions on the screen.
    def addInstructions(self, pos, msg):
        return OnscreenText(text=msg, style=1, fg=(1,1,1,1), mayChange=1,
                            pos=(-1.3, pos), align=TextNode.ALeft, scale = .05, shadow=(0,0,0,1), shadowOffset=(0.1,0.1))
    
    # Function to put title on the screen.
    def addTitle(self, text):
        return OnscreenText(text=text, style=1, fg=(1,1,1,1),
                            pos=(1.3,-0.95), align=TextNode.ARight, scale = .07)
