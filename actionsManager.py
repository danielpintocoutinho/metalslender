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

		self.point0 = loader.loadModel("assets/models/sphere")
		self.point0.setScale(0.05)
		self.point0.setPos(Vec3(0,-1,0))
		#self.point0.reparentTo(render)
		
		self.doors = [Door(base, room,Vec3(5.0, -0.08, -0.9), Vec3(0, 0, 0), 87), \
					  Door(base, room,Vec3(7.99263, -0.204471, -0.9), Vec3(-90, 0, 0), 90), \
					  Door(base, room,Vec3(8.05, -1.5654, -0.9), Vec3(0, 0, 0), -85), \
					  Door(base, room,Vec3(14, -0.077, -0.7), Vec3(0, 0, 0), 90), \
					  Door(base, room,Vec3(15.36, -0.05, -0.7), Vec3(90, 0, 0), -87), \
		              Door(base, room,Vec3(15.34, 1.07, -0.7), Vec3(125, 0, 0), -117), \
#TODO: Uncomment these
 		              Gate(base, rooms[1],Vec3(7.49425, -146.543, -0.8158868), Vec3(180, 0, 0), 90), \
 					  Gate(base, rooms[1],Vec3(1.91029, -146.543, -0.8158868), Vec3(0, 0, 0), -90)
		              ]
		
#TODO: Uncomment these
		self.lock = Lock(base, rooms[1].root,"assets/chicken/cadeado","assets/sounds/items/keys.mp3",Vec3(4.7, -146.3, 0), Vec3(0, 0, 0), [self.doors[6],self.doors[7]])
		self.locked_doors = [LockedDoor(base, room,Vec3(5.1, -6.07342, -0.09), Vec3(180, 0, 0), -90, rooms[1], 0)]

		self.keys = [Collectible(base, room,"assets/chicken/key","assets/sounds/items/keys.mp3",Vec3(16.31,-2.7,-0.31), Vec3(0, 0, 0)), \
		             Collectible(base, room,"assets/chicken/key","assets/sounds/items/keys.mp3",Vec3(-4.57284, 0.596583, 8), Vec3(180, 0, -90)), \
		             Collectible(base, room,"assets/chicken/key","assets/sounds/items/keys.mp3",Vec3(2.94139, 3.77321, 6.1), Vec3(90, 0, 0)), \
		             Collectible(base, room,"assets/chicken/key","assets/sounds/items/keys.mp3",Vec3(16.6, 1.83443, -0.98), Vec3(0, 0, 0))]
		
# <<<<<<< HEAD
		#visualize direction
# 		self.accept("u", self.hide)
# 		self.accept("i", self.show)
# 		
# 		self.point0.getNodePath().hide()
# 		
# 	def __del__(self):
# 		self.base   = None
# 		self.player = None
# 		self.point0 = None
# 		del self.doors [:]
# 		del self.locked_doors [:]
# 		del self.keys [:]
# =======
	
	def update(self):
		self.center = self.player.getNodePath().getPos()
		
		ang1 = self.base.cam.getHpr().getY()*(3.141592/180)
		ang2 = self.player.getNodePath().getHpr().getX()*(3.141592/180)
		vec_cen = Vec3(self.center.getX(),self.center.getY()+0.5,self.center.getZ()) - self.center
		
		rot1 = Vec3(vec_cen.getX(), vec_cen.getY()*cos(ang1) + vec_cen.getZ()*sin(ang1), vec_cen.getY() * sin(ang1) + vec_cen.getZ()*cos(ang1))
		rot2 = Vec3(rot1.getX()*cos(ang2) - rot1.getY()*sin(ang2), rot1.getX() * -sin(ang2) + rot1.getY()*cos(ang2), rot1.getZ())
		
		self.hand = rot2 + self.center
		self.hand.setZ(self.hand.getZ() + self.base.cam.getPos().getZ())
	
		self.point0.setPos(self.hand)
		
		print("player: ",self.player.getNodePath().getPos())
		
	def act(self):
		
		self.update()
		
		for i in range(len(self.doors)):
			if(self.doors[i].act_dist(self.hand) < 0.5):
				self.doors[i].act()
				return
		
		for i in range(len(self.keys)):
			if(self.keys[i].act_dist(self.hand) < 0.5):
				self.keys[i].act()
				return
				
		for i in range(len(self.locked_doors)):
			if(self.locked_doors[i].act_dist(self.hand) < 0.5):
				self.locked_doors[i].act(self.keys[self.locked_doors[i].keyId])
				return
				
		if(self.lock.act_dist(self.hand) < 0.5):
			self.lock.act(self.keys[1])
	
	def diff_dir(self, point):
		v = self.center - self.point
		u = self.center - point.getPos()
		
		return (u - u.project(v)).length()
		
	def diff_dist(self, point):	
		return (point.getPos() - self.point).length()

	def addDoors(self, base, room, doors):
# 		print "numero de portas: ", len(doors)
		for door in doors:
			newDoor = Door(base, room, door.getPos(render), Vec3(-90, 0, 0), 90)
			self.doors.append(newDoor)

	def addKeys(self, base, room, keys):
# 		print "numero de chaves: ", len(keys)
		for key in keys:
			newKey = Collectible(base, room,"assets/chicken/key","assets/sounds/items/keys.mp3",key.getPos(render), Vec3(0, 0, 0))
			self.keys.append(newKey)