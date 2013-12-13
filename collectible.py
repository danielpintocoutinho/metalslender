from panda3d.core import *
from math import *
import sys,os

from direct.showbase.DirectObject import DirectObject
from direct.showbase import Audio3DManager
from direct.task import Task
from direct.interval.IntervalGlobal import Sequence

import scene_obj

class Collectible(DirectObject):
	
	def __init__(self,base, fatherNode,path,pathSound, pos, hpr):
		self.audio3d = Audio3DManager.Audio3DManager(base.sfxManagerList[0], base.cam)
		
		self.model = base.loader.loadModel(path)

		self.room = fatherNode
		self.model.reparentTo(self.room)
		self.model.setPos(pos)
		self.model.setHpr(hpr)
		
		self.pickedSound = self.audio3d.loadSfx(pathSound)
		
		self.picked = False
		
	def act(self):
		self.pickedSound.play()
		self.model.detachNode()
		self.picked = True
				
	def act_dist(self, hand):
		return (hand - self.model.getPos(self.room)).length()
		
	def wasPicked(self):
		return self.picked

	def used(self):
		self.picked = False

	def clean(self):
		#self.audio3d.unloadSfx(self.pickedSound)
		self.audio3d.disable()