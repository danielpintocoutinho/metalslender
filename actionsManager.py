from panda3d.core import *
from math import *
import sys,os

from direct.showbase.DirectObject import DirectObject
from direct.showbase import Audio3DManager
from direct.task import Task

import scene_obj

from door import Door
from lockedDoor import LockedDoor
from collectible import Collectible

class ActionManager(DirectObject):
	
	
	def __init__(self, base, room):
		
		self.player = None
		
		self.center = Vec3(0,0,0)		
		self.hand  = Vec3(0,0,0)
		self.point0 = scene_obj.SceneObj("act_point0","assets/models/sphere", base.render, self.hand, 1)
		
		self.doors = [Door(base, room,Vec3(101, 32, 0), Vec3(-90, 0, 0), 90), \
					  Door(base, room,Vec3(40, 35, 0), Vec3(0, 0, 0), 90), \
					  Door(base, room,Vec3(102, 4.5, 0), Vec3(0, 0, 0), -85), \
					  Door(base, room,Vec3(222.5, 35, 5.1), Vec3(0, 0, 0), 90), \
					  Door(base, room,Vec3(250, 37, 5.1), Vec3(90, 0, 0), -87), \
		              Door(base, room,Vec3(249.5, 58.5, 5.1), Vec3(125, 0, 0), -117)]
		              
		self.locked_doors = [LockedDoor(base, room,Vec3(35, -45, 0), Vec3(180, 0, 0), -90)]
		
		self.keys = [Collectible(base, room,"assets/chicken/key","assets/sounds/items/keys.mp3",Vec3(266.57, -19.85, 7.32), Vec3(0, 0, 0))]
		
		#visualize direction
		self.accept("u", self.hide)
		self.accept("i", self.show)
		
		self.point0.model.hide()
		
	
	def update(self):
		self.center = self.player.getNodePath().getPos()
		
		ang1 = base.cam.getHpr().getY()*(3.141592/180)
		ang2 = self.player.getNodePath().getHpr().getX()*(3.141592/180)
		vec_cen = Vec3(self.center.getX(),self.center.getY()+15,self.center.getZ()) - self.center
		
		rot1 = Vec3(vec_cen.getX(), vec_cen.getY()*cos(ang1) + vec_cen.getZ()*sin(ang1), vec_cen.getY() * sin(ang1) + vec_cen.getZ()*cos(ang1))
		rot2 = Vec3(rot1.getX()*cos(ang2) - rot1.getY()*sin(ang2), rot1.getX() * -sin(ang2) + rot1.getY()*cos(ang2), rot1.getZ())
		
		self.hand = rot2 + self.center
		self.hand.setZ(self.hand.getZ() + base.cam.getPos().getZ() - 5)
	
		self.point0.model.setPos(self.hand)
					
		
	def act(self):
		
		self.update()
		
		for i in range(len(self.doors)):
			if(self.doors[i].act_dist(self.hand) < 8):
				self.doors[i].act()
				return
		
		for i in range(len(self.keys)):
			if(self.keys[i].act_dist(self.hand) < 8):
				self.keys[i].act()
				return
				
		for i in range(len(self.locked_doors)):
			if(self.locked_doors[i].act_dist(self.hand) < 8):
				self.locked_doors[i].act(self.keys[i])
				return
		
	def hide(self):
		self.point0.model.hide()
		
	def show(self):
		self.point0.model.show()
	
	def diff_dir(self, point):
		v = self.center - self.point
		u = self.center - point.getPos()
		
		return (u - u.project(v)).length()
		
	def diff_dist(self, point):	
		return (point.getPos() - self.point).length()
		
	def setPlayer(self, player):
		self.player = player		

