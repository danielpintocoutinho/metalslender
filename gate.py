from panda3d.core import *
from math import *
import sys,os

from direct.showbase.DirectObject import DirectObject
from direct.showbase import Audio3DManager
from direct.task import Task
from direct.interval.IntervalGlobal import Sequence

import scene_obj

class Gate(DirectObject):
	
	def __init__(self, base, fatherNode, pos, hpr, angle):
		
		self.model = base.loader.loadModel("assets/chicken/portao")
		self.knob = self.model.attachNewNode("knob")
		self.knob.setPos(Vec3(50,0,12))
		self.knob.reparentTo(self.model)
		self.room = fatherNode.model
		self.model.reparentTo(self.room)
		self.model.setPos(pos)
		self.model.setHpr(hpr)
		self.model.setScale(0.05)
		
		self.closeAngle = hpr.getX()
		self.openAngle  = hpr.getX() + angle

		self.openInterval  = self.model.hprInterval(1.6,Vec3(self.openAngle,0,0))
		self.closeInterval = self.model.hprInterval(1.6,Vec3(self.closeAngle,0,0))
		
		self.forceSound  = loader.loadSfx('assets/sounds/items/gate_force.mp3')
		self.openSound   = loader.loadSfx('assets/sounds/items/gate_open.mp3')
		self.closeSound  = loader.loadSfx('assets/sounds/items/gate_close.mp3')
		
		self.closed = 1
		self.locked = 1
		
	def act(self):
		
		#Test if the player has the key
		if (self.locked):
			
			self.forceSound.play()			
			return
		
		if (self.model.getHpr().getX() == self.openAngle or \
		    self.model.getHpr().getX() == self.closeAngle):
			
			if (self.closed):
				self.openInterval.start()
				self.openSound.play()
				self.closed = 0
			else:
				self.closeInterval.start()
				self.closeSound.play()
				self.closed = 1
				
	def act_dist(self, hand):
		return (hand - self.knob.getPos(self.room)).length()
		
	def unlock(self):
		self.locked = 0		

	def clean(self):
		pass
