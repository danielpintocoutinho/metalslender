from panda3d.core import *
from math import *
import sys,os

from direct.showbase.DirectObject import DirectObject
from direct.showbase import Audio3DManager
from direct.task import Task
from direct.interval.IntervalGlobal import Sequence

import scene_obj

class Lock(DirectObject):
	
	def __init__(self,base, fatherNode,path,pathSound, pos, hpr, doors):
		
		self.model = base.loader.loadModel(path)

		self.room = fatherNode
		self.model.reparentTo(self.room)
		self.model.setPos(pos)
		self.model.setHpr(hpr)
		
		self.doors = doors 
		
		self.pickedSound = loader.loadSfx(pathSound)
		
		self.picked = False
		
	def act(self, key):
		
		if (self.picked):
			return
		
		if (key.wasPicked()):
			key.used()
			self.pickedSound.play()
			self.model.detachNode()
			self.picked = True
					
			for i in range(len(self.doors)):
				self.doors[i].unlock()

				
	def act_dist(self, hand):
		print ("dist2: ", (hand - self.model.getPos(self.room)).length())
		return (hand - self.model.getPos(self.room)).length()
		
	def wasPicked(self):
		return self.picked

	def used(self):
		self.picked = False

