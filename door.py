from panda3d.core import *
from math import *
import sys,os

from direct.showbase.DirectObject import DirectObject
from direct.showbase import Audio3DManager
from direct.task import Task
from direct.interval.IntervalGlobal import Sequence

from scene_obj import *
from collision import CollisionMask

class Door(DirectObject):
	
	def __init__(self, base, fatherNode, pos, hpr, angle):
		
		self.model = base.loader.loadModel("assets/chicken/porta")
		self.knob  = base.loader.loadModel("assets/chicken/knob")
		self.knob.setPos(Vec3(17.6,0,8))
		self.knob.reparentTo(self.model)
		self.room = fatherNode
		self.model.reparentTo(self.room)
		self.model.setPos(pos)
		self.model.setHpr(hpr)
		self.model.setScale(0.05)


		"""self.modelBody = self.model.attachNewNode(CollisionNode("door"))
		self.modelBody.node().addSolid(CollisionTube(10, 0, -10, 10, 0, 0, 4))
		self.modelBody.node().setFromCollideMask(CollisionMask.NONE)
		self.modelBody.node().setIntoCollideMask(CollisionMask.DOOR)"""
		
		self.closeAngle = hpr.getX()
		self.openAngle  = hpr.getX() + angle

		self.openInterval  = self.model.hprInterval(1.6,Vec3(self.openAngle,0,0))
		self.closeInterval = self.model.hprInterval(1.6,Vec3(self.closeAngle,0,0))
		
		knobInterval1  = self.knob.hprInterval(0.3,Vec3(0,0,-45))
		knobInterval2  = self.knob.hprInterval(0.1,Vec3(0,0,0))
		self.knobSequence = Sequence(knobInterval1,knobInterval2)
		
		self.openSound  = loader.loadSfx('assets/sounds/items/door_open.mp3')
		self.closeSound = loader.loadSfx('assets/sounds/items/door_close.mp3')
		#self.point0 = scene_obj.SceneObj("knob0","assets/models/sphere", self.knob, 1)
		
		self.closed = 1
		
	def act(self):
		
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

	def clean(self):
		#self.audio3d.unloadSfx(self.openSound)
		#self.audio3d.unloadSfx(self.closeSound)
		#self.audio3d.disable()
		pass
