from panda3d.core import *
from math import *
import sys,os

from direct.showbase.DirectObject import DirectObject
from direct.showbase import Audio3DManager
from direct.task import Task

import scene_obj

from actionsManager import ActionManager

class EventManager(DirectObject):
	
	
	def __init__(self, base, player, itemList):
		
		self.player = player
		self.items  = itemList
		self.base = base
		
		self.center = Vec3(0,0,0)
		
		self.draw = 1
		
		self.vision  = Vec3(0,20,-10)
		
		#Pontos chave para os sustos
		self.point0 = scene_obj.SceneObject(base, "point0", "assets/models/sphere", base.render, self.vision, 1)
		self.point1 = scene_obj.SceneObject(base, "point1", "assets/models/sphere", base.render, Vec3(100,25,10), 1)
		self.point2 = scene_obj.SceneObject(base, "point2", "assets/models/sphere", base.render, Vec3(160,20,15), 1)
		self.point3 = scene_obj.SceneObject(base, "point3", "assets/models/sphere", base.render, Vec3(280,70,15), 1)
		self.point1.root.detachNode()
		self.point2.root.detachNode()
		
		self.scared1 = 0
		self.scared2 = 0
		self.scared3 = 0
		self.vol     = 1
		
		self.scare   = base.loader.loadSfx("assets/sounds/scare/scare2.mp3")
		self.tension = base.loader.loadSfx("assets/sounds/scare/tension/tension.mp3")
		
		self.firstEnemy = base.loader.loadModel("assets/chicken/hooded")
		self.firstEnemy.setPos(Vec3(220,-20,-10))
		self.firstEnemy.setScale(8)
		self.firstEnemy.reparentTo(base.render)
		self.enemyInterval = self.firstEnemy.posInterval(0.8,Vec3(220,80,-10),startPos = Vec3(220,-20,-10))
		
		#visualize direction
		self.accept("h", self.hide)
		self.accept("j", self.show)
		
		self.point0.getNodePath().removeNode()
		
	
	def update(self, task):
		self.center = self.player.root.getPos()
		
		ang1 = self.base.cam.getHpr().getY()*(3.141592/180)
		ang2 = self.player.root.getHpr().getX()*(3.141592/180)
		vec_cen = Vec3(self.center.getX(),self.center.getY()+30,self.center.getZ()) - self.center
		
		rot1 = Vec3(vec_cen.getX(), vec_cen.getY()*cos(ang1) + vec_cen.getZ()*sin(ang1), vec_cen.getY() * sin(ang1) + vec_cen.getZ()*cos(ang1))
		rot2 = Vec3(rot1.getX()*cos(ang2) - rot1.getY()*sin(ang2), rot1.getX() * -sin(ang2) + rot1.getY()*cos(ang2), rot1.getZ())
		
		self.vision = rot2 + self.center
		self.vision.setZ(self.vision.getZ() + self.base.cam.getPos().getZ())
		
		if not self.point0.getNodePath().isEmpty():
			self.point0.getNodePath().setPos(self.vision)
		
		if (self.center.getX() > 100):
			if (self.tension.status() != self.tension.PLAYING):
				self.tension.setPlayRate(0.6)
				self.tension.setLoop(True)
				self.tension.play()
			else:
				if (self.tension.getVolume() < 1):
					self.vol += 0.01
					self.tension.setVolume(self.vol)
		else:
			if (self.tension.status() == self.tension.PLAYING):
				self.tension.setVolume(self.vol)
				self.vol -= 0.005
				if (self.vol <= 0):
					self.tension.stop()			
		
		#TODO: improve player's aiming detection system  
		#1- Susto : corredor para a cozinha
		if (not self.scared1 and (self.diff_dist(self.point2.getNodePath()) < 5) and (self.diff_dir(self.point2.getNodePath())) < 10):
			self.enemyInterval.start()
			self.scared1 = 1
			self.scare.play()
			self.player.scream()
			
		#2- Susto : banheiro
		if (not self.scared2 and not self.items.doors[5].closed  and (self.diff_dist(self.point3.getNodePath()) < 30) and (self.diff_dir(self.point3.getNodePath())) < 14):
			self.scared2 = 1
			self.scare.play()
			self.player.scream()
		
		#print "##"
		#print("eve:",self.point.getX(),self.point.getY(),self.point.getZ())
		#print("eve:",self.center.getX(),self.center.getY(),self.center.getZ())
		print self.diff_dist(self.base.render.find("point3"))
		print self.diff_dir(self.base.render.find("point3"))
			
		return Task.cont
		
		
	def hide(self):
		self.point0.model.hide()
		
	def show(self):
			self.point0.model.show()	
	
	def diff_dir(self, point):
		v = self.center - self.vision
		u = self.center - point.getPos()
		
		return (u - u.project(v)).length()
		
	def diff_dist(self, point):		
		return (point.getPos() - self.vision).length()		
	
	def start(self):
		self.base.taskMgr.add(self.update, "update-task")
