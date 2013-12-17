from panda3d.core import *
from math import *
import sys,os

from direct.showbase.DirectObject import DirectObject
from direct.showbase import Audio3DManager
from direct.task import Task

import scene_obj

from door import Door
from lockedDoor import LockedDoor
from gate import Gate
from lock import Lock
from collectible import Collectible

class ActionManager(DirectObject):
	
	def __init__(self, base, room, player,rooms):
		
		self.base   = base
		self.player = player
		
		self.center = Vec3(0,0,0)		
		self.hand   = Vec3(0,0,0)
		self.point0 = scene_obj.SceneObject(base, "act_point0","assets/models/sphere", base.render, self.hand, 1)
		
		self.doors = [Door(base, room,Vec3(5.006, -0.08, -0.58), Vec3(-90, 0, 0), 90), \
					  Door(base, room,Vec3(38, 35, 0), Vec3(0, 0, 0), 90), \
					  Door(base, room,Vec3(100, 4.5, 0), Vec3(0, 0, 0), -85), \
					  Door(base, room,Vec3(220.5, 35, 5.1), Vec3(0, 0, 0), 90), \
					  Door(base, room,Vec3(248, 37, 5.1), Vec3(90, 0, 0), -87), \
		              Door(base, room,Vec3(247.5, 58.5, 5.1), Vec3(125, 0, 0), -117), \
		              Gate(base, rooms[1],Vec3(87.8, -2893.36, 0), Vec3(180, 0, 0), 90), \
					  Gate(base, rooms[1],Vec3(-23.46, -2893.36, 0), Vec3(0, 0, 0), -90)
		              ]
		
		self.lock = Lock(base, rooms[1].root,"assets/chicken/cadeado","assets/sounds/items/keys.mp3",Vec3(30, -2891.36, 5), Vec3(0, 0, 0), [self.doors[6],self.doors[7]])

		self.locked_doors = [LockedDoor(base, room,Vec3(35, -85, 10), Vec3(180, 0, 0), -90, rooms[1], 0)]
		#self.locked_doors = []

		self.keys = [Collectible(base, room,"assets/chicken/key","assets/sounds/items/keys.mp3",Vec3(16.31,-2.7,-0.31), Vec3(0, 0, 0)), \
		             Collectible(base, room,"assets/chicken/key","assets/sounds/items/keys.mp3",Vec3(0, 0, 0), Vec3(0, 0, 0))]
		
		#visualize direction
		self.accept("u", self.hide)
		self.accept("i", self.show)
		
		self.point0.getNodePath().hide()
	
	def update(self):
		self.center = self.player.getNodePath().getPos()
		
		ang1 = self.base.cam.getHpr().getY()*(3.141592/180)
		ang2 = self.player.getNodePath().getHpr().getX()*(3.141592/180)
		vec_cen = Vec3(self.center.getX(),self.center.getY()+3,self.center.getZ()) - self.center
		
		rot1 = Vec3(vec_cen.getX(), vec_cen.getY()*cos(ang1) + vec_cen.getZ()*sin(ang1), vec_cen.getY() * sin(ang1) + vec_cen.getZ()*cos(ang1))
		rot2 = Vec3(rot1.getX()*cos(ang2) - rot1.getY()*sin(ang2), rot1.getX() * -sin(ang2) + rot1.getY()*cos(ang2), rot1.getZ())
		
		self.hand = rot2 + self.center
		self.hand.setZ(self.hand.getZ() + self.base.cam.getPos().getZ() - 5)
	
		self.point0.getNodePath().setPos(self.hand)
		
		print("h: ",self.hand,self.point0.getNodePath().getPos())
		
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
				self.locked_doors[i].act(self.keys[self.locked_doors[i].keyId])
				return
				
		if(self.lock.act_dist(self.hand) < 12):
			self.lock.act(self.keys[1])
		
	def hide(self):
		self.point0.getNodePath().hide()
		
	def show(self):
		#self.point0.getNodePath().show()
		pass
	
	def diff_dir(self, point):
		v = self.center - self.point
		u = self.center - point.getPos()
		
		return (u - u.project(v)).length()
		
	def diff_dist(self, point):	
		return (point.getPos() - self.point).length()


	def addDoors(self, base, room, doors):
		print "numero de portas: ", len(doors)
		for door in doors:
			newDoor = Door(base, room, door.getPos(render), Vec3(-90, 0, 0), 90)
			self.doors.append(newDoor)

	def addKeys(self, base, room, keys):
		print "numero de chaves: ", len(keys)
		for key in keys:
			newKey = Collectible(base, room,"assets/chicken/key","assets/sounds/items/keys.mp3",key.getPos(render), Vec3(0, 0, 0))
			self.keys.append(newKey)
