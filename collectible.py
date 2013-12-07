from panda3d.core import *
from math import *
import sys,os

from direct.showbase.DirectObject import DirectObject
from direct.showbase import Audio3DManager
from direct.task import Task
from direct.interval.IntervalGlobal import Sequence

import scene_obj

audio3d = Audio3DManager.Audio3DManager(base.sfxManagerList[0], camera)

class Collectible(DirectObject):
	
	def __init__(self,fatherNode,path,pathSound, pos, hpr):
		
		self.model = loader.loadModel(path)

		self.room = fatherNode
		self.model.reparentTo(self.room)
		self.model.setPos(pos)
		self.model.setHpr(hpr)
		
		self.pickedSound = audio3d.loadSfx(pathSound)
		
		self.picked = 0
		
	def act(self):
		self.pickedSound.play()
		self.model.detachNode()
		self.picked = 1
				
	def act_dist(self, hand):
		return (hand - self.model.getPos(self.room)).length()
		
	def wasPicked(self):
		return self.picked
