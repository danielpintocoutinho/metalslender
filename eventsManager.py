from panda3d.core import *
from math import *
import sys,os
import random

from direct.showbase.DirectObject import DirectObject
from direct.showbase import Audio3DManager
from direct.task import Task

import scene_obj

from actionsManager import ActionManager


class EventManager(DirectObject):
	
	
	def __init__(self, base, player, itemList, rooms):
		
		self.player = player
		self.items  = itemList
		self.rooms  = rooms
		self.base   = base
		
		self.center = Vec3(0,0,0)
		
		self.draw = 1
		
		self.vision = Vec3(0,4,0)
		self.back   = Vec3(0,-4,0)
		
		#Pontos chave para os sustos
		self.point0 = loader.loadModel("assets/models/sphere")
		self.point0.setScale(0.05)
		self.point0.setPos(Vec3(0,0,0))
		#self.point0.reparentTo(render)
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
		self.incFear = 0;
		
		self.firstEnemy = base.loader.loadModel("vulto")
		self.firstEnemy.setPos(Vec3(14.3458, -2.58647, -1))
		self.firstEnemy.setHpr(180,0,0)
		self.firstEnemy.setScale(0.09)
		self.firstEnemy.reparentTo(base.render)
		self.firstEnemy.hide()
		self.enemyInterval = None
		self.enemyInterval2 = None
		
		self.accept("p", self.test)	
	
	def update(self, task):
		self.center = self.player.root.getPos()
		
		ang1 = self.base.cam.getHpr().getY()*(3.141592/180)
		ang2 = self.player.root.getHpr().getX()*(3.141592/180)
		vec_cen = Vec3(self.center.getX(),self.center.getY()+2,self.center.getZ()) - self.center
		
		rot1 = Vec3(vec_cen.getX(), vec_cen.getY()*cos(ang1) + vec_cen.getZ()*sin(ang1), vec_cen.getY() * sin(ang1) + vec_cen.getZ()*cos(ang1))
		rot2 = Vec3(rot1.getX()*cos(ang2) - rot1.getY()*sin(ang2), rot1.getX() * -sin(ang2) + rot1.getY()*cos(ang2), rot1.getZ())
		
		self.vision = rot2 + self.center
		self.vision.setZ(self.vision.getZ() + self.base.cam.getPos().getZ())
		
		vec_cen = Vec3(self.center.getX(),self.center.getY()-10,self.center.getZ()) - self.center
		
		rot1 = Vec3(vec_cen.getX(), vec_cen.getY()*cos(ang1) + vec_cen.getZ()*sin(ang1), vec_cen.getY() * sin(ang1) + vec_cen.getZ()*cos(ang1))
		rot2 = Vec3(rot1.getX()*cos(ang2) - rot1.getY()*sin(ang2), rot1.getX() * -sin(ang2) + rot1.getY()*cos(ang2), rot1.getZ())
		
		self.back = rot2 + self.center
		self.back.setZ(self.back.getZ() + self.base.cam.getPos().getZ())
		
		self.point0.setPos(self.vision)
		
		
		#hide blocoH 2-andar
		if (self.player.root.getZ() > 2.3):
			if (self.rooms[2].root.isHidden()):
				self.rooms[2].root.show()
		else:
			if (not self.rooms[2].root.isHidden()):
				self.rooms[2].root.hide()
		
		if (self.center.getX() > 8):
			if (self.tension.status() != self.tension.PLAYING):
				self.tension.setPlayRate(0.6)
				self.tension.setLoop(True)
				self.tension.play()
			else:
				if (self.tension.getVolume() < 1):
					self.vol += 0.01
					self.tension.setVolume(self.vol)
		
		#increase fear
		if (self.incFear):
			self.player.fear = min(self.player.fear + 0.05, 1.0)
			if (self.player.fear > 0.99):
				#filters.delBlurSharpen()
				self.incFear = 0;

		#TODO: improve player's aiming detection system  

		#1- Susto : corredor para a cozinha
		#if (not self.scared1 and (self.diff_dist(self.point2.getNodePath()) < 5) and (self.diff_dir(self.point2.getNodePath())) < 10):
		if (not self.scared1 and self.player.root.getPos().getX() > 10):
			self.firstEnemy.setHpr(180,0,0)
			self.firstEnemy.show()
			self.enemyInterval = self.firstEnemy.posInterval(1,Vec3(14.3458, 8, 0),startPos = Vec3(14.3458, -2.58647, 0))
			self.enemyInterval.start()
			self.scared1 = 1
			self.scare.play()
			#self.incFear = 1;
			
		#2- Susto : banheiro
		if (not self.scared2 and self.player.root.getPos().getX() > 15.3 and self.player.root.getPos().getY() > 1.3):
			self.scared2 = 1
			self.firstEnemy.setPos(self.vision)
			self.firstEnemy.setHpr(Vec3(self.player.root.getHpr().getX(), self.base.cam.getHpr().getY(), 0))
			self.firstEnemy.show()
			self.enemyInterval2 = self.firstEnemy.posInterval(1.5,self.back,startPos = self.firstEnemy.getPos())
			self.enemyInterval2.start()
			self.scare.play()
			self.player.die()
			
		if (self.scared2 and not self.enemyInterval2.isPlaying()):
			self.firstEnemy.hide()

		return Task.cont

	def test(self):
		self.firstEnemy.setPos(self.back)
		self.firstEnemy.setHpr(Vec3(self.player.root.getHpr().getX(), self.base.cam.getHpr().getY(), 0))
		self.firstEnemy.show()
	
	def diff_dir(self, point):
		v = self.center - self.vision
		u = self.center - point.getPos()
		
		return (u - u.project(v)).length()
		
	def diff_dist(self, point):		
		return (point.getPos() - self.vision).length()		
	
	def start(self):
		self.base.taskMgr.add(self.update, "update-task")

	def destroy(self):
		self.point0.root.removeNode()
		self.point1.root.removeNode()
		self.point2.root.removeNode()
		self.point3.root.removeNode()
		self.firstEnemy.removeNode()

		base.loader.unloadSfx(self.scare)
		base.loader.unloadSfx(self.tension)



