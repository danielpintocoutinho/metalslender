from panda3d.core import *
from math import *
import sys,os

from direct.showbase.DirectObject import DirectObject
from direct.showbase import Audio3DManager
from direct.task import Task

import scene_obj

class EventManager(DirectObject):
	
	
	def __init__(self, player):
		
		self.player = player;
		
		self.center = Vec3(0,0,0)
		
		self.draw = 1
		
		self.point  = Vec3(0,20,-10)
		self.point0 = scene_obj.SceneObj("point0","assets/models/sphere", self.point, 1)
		self.point1 = scene_obj.SceneObj("point1","assets/models/sphere", Vec3(250,30,15), 1)
		self.point2 = scene_obj.SceneObj("point2","assets/models/sphere", Vec3(100,25,10), 1)
		
		self.scared  = 0
		self.vol     = 1
		self.scare   = loader.loadSfx("assets/sounds/scare/scare2.mp3")
		self.tension = loader.loadSfx("assets/sounds/scare/tension/tension.mp3")
		
		#visualize direction
		self.accept("h", self.hide)
		self.accept("j", self.show)
		
		self.point0.model.detachNode()
		
	
	def update(self, task):
		self.center = self.player.getNodePath().getPos()
		
		ang1 = base.cam.getHpr().getY()*(3.141592/180)
		ang2 = self.player.getNodePath().getHpr().getX()*(3.141592/180)
		vec_cen = Vec3(self.center.getX(),self.center.getY()+30,self.center.getZ()) - self.center
		
		rot1 = Vec3(vec_cen.getX(), vec_cen.getY()*cos(ang1) + vec_cen.getZ()*sin(ang1), vec_cen.getY() * sin(ang1) + vec_cen.getZ()*cos(ang1))
		rot2 = Vec3(rot1.getX()*cos(ang2) - rot1.getY()*sin(ang2), rot1.getX() * -sin(ang2) + rot1.getY()*cos(ang2), rot1.getZ())
		
		self.point = rot2 + self.center
		self.point.setZ(self.point.getZ() + 25)
		
		if (self.point0.model.hasParent()):
			render.find("point0").setPos(self.point)
		
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
		
		if (not self.scared and (self.diff_dist(render.find("point1")) < 20) and (self.diff_dir(render.find("point1")) < 10)):
			self.scared = 1
			self.scare.play()
			self.player.scream()
			self.player.fear = min(self.player.fear + 1.2, 1.0)
		
		#print "##"
		#print self.diff_dist(render.find("point1"))
		#print self.diff_dir(render.find("point1"))
			
		return Task.cont
		
		
	def hide(self):
		self.point0.model.detachNode()
		
	def show(self):
		if (not self.point0.model.hasParent()):
			self.point0.model.reparentTo(self.point0.modelNP)	
	
	def diff_dir(self, point):
		v = self.center - self.point
		u = self.center - point.getPos()
		
		return (u - u.project(v)).length()
		
	def diff_dist(self, point):		
		return (point.getPos() - self.point).length()		
	
	def start(self):
		taskMgr.add(self.update, "update-task")

