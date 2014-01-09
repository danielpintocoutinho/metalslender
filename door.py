from panda3d.core import *
from math import *
import sys,os

from direct.actor.Actor import Actor

from direct.showbase.DirectObject import DirectObject
from direct.showbase import Audio3DManager
from direct.task import Task
from direct.interval.IntervalGlobal import Sequence

from constants import *
from scene_obj import *
from collision import CollisionMask

class Door(Actor):
	
	def __init__(self, base, model, anim, key='', closed=True):
		Actor.__init__(self, model, anim)
		
		self.openSound  = base.loader.loadSfx('assets/sounds/items/door_open.mp3')
		self.closeSound = base.loader.loadSfx('assets/sounds/items/door_close.mp3')
		
		self.key    = key
		self.locked = bool(key)
		self.closed = closed
		
	#TODO: Doors must be reset, not removed
	def __del__(self):
 		self.removeNode()
		self.openSound = None
		self.closeSound = None
# 		self.knobSequence = None
		
	#TODO: include keys usage
	def act(self):
		
		if self.closed:
			self.openSound.play()
			self.play('Open')
		else:
			self.closeSound.play()
			self.play('Close')
			
		self.closed = not self.closed

	def clean(self):
		#self.audio3d.unloadSfx(self.openSound)
		#self.audio3d.unloadSfx(self.closeSound)
		#self.audio3d.disable()
		pass