from panda3d.core import *
from math import *
import sys,os

from direct.showbase.DirectObject import DirectObject
from direct.showbase import Audio3DManager
from direct.task import Task
from direct.interval.IntervalGlobal import Sequence

import scene_obj

class LockedDoor(DirectObject):
	
	def __init__(self, base, fatherNode, pos, hpr, angle, lockedRoom, keyId):
		
		audio3d = Audio3DManager.Audio3DManager(base.sfxManagerList[0], base.cam)
		
		self.model = base.loader.loadModel("assets/chicken/porta_entrada_lcg")
		self.knob  = base.loader.loadModel("assets/chicken/knob")
		self.knob.setPos(Vec3(26,0,0))
		self.knob.reparentTo(self.model)
		self.room = fatherNode
		self.model.reparentTo(self.room)
		self.model.setPos(pos)
		self.model.setHpr(hpr)
		self.model.setScale(0.05)
		self.lockedRoom = lockedRoom
		self.keyId = keyId
		
		self.closeAngle = hpr.getX()
		self.openAngle  = hpr.getX() + angle

		self.openInterval  = self.model.hprInterval(1.6,Vec3(self.openAngle,0,0))
		self.closeInterval = self.model.hprInterval(1.6,Vec3(self.closeAngle,0,0))
		
		knobInterval1  = self.knob.hprInterval(0.3,Vec3(0,0,-45))
		knobInterval2  = self.knob.hprInterval(0.1,Vec3(0,0,0))
		self.knobSequence = Sequence(knobInterval1,knobInterval2)
		
		self.forceSound  = loader.loadSfx('assets/sounds/items/door_force.mp3')
		self.unlockSound = loader.loadSfx('assets/sounds/items/door_unlock.mp3')
		self.openSound   = loader.loadSfx('assets/sounds/items/door_open.mp3')
		self.closeSound  = loader.loadSfx('assets/sounds/items/door_close.mp3')
		
		self.closed = 1
		self.locked = 1
		
	def __del__(self):
		self.room = None
		self.model.removeNode()
		self.knob.removeNode()
		self.openSound = None
		self.closeSound = None
		self.forceSound = None
		self.unlockSound = None
		
	def act(self, key):
		
		#Test if the player has the key
		if (self.locked):
			
			if (key.wasPicked()):
				self.lockedRoom.root.reparentTo(render)
				key.used()
				key.pickedSound.play()
				self.unlockSound.play()
				self.locked = 0
			else:
				self.forceSound.play()
			
			return
		
		if (self.model.getHpr().getX() == self.openAngle or \
		    self.model.getHpr().getX() == self.closeAngle):
			
			if (self.closed):
				self.openInterval.start()
				self.knobSequence.start()
				self.openSound.play()
				self.closed = 0
			else:
				self.closeInterval.start()
				self.closeSound.play()
				self.closed = 1
				
	def act_dist(self, hand):
		return (hand - self.knob.getPos(self.room)).length()
