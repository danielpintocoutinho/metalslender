import panda3d
import sys,os

from pandac.PandaModules import ActorNode, CollisionHandlerQueue, CollisionHandlerGravity, CollisionHandlerPusher, CollisionNode, CollisionSphere, CollisionTraverser, BitMask32, CollisionRay
from pandac.PandaModules import Vec3
from direct.interval.IntervalGlobal import *
from direct.actor import Actor
from direct.task.Task import Task
from random import *
from collisionSystem import *

class Room:

	def __init__(self, base, name, model, scene, pos=Vec3(0,0,0), scale=1.0):
		self.base = base
		
		#TODO: The modelpath could be the model itself
		self.modelNP = scene.attachNewNode(name)
		self.model = base.loader.loadModel(model)
		self.model.reparentTo(self.modelNP)
		
		self.modelNP.setPos(pos)
		self.modelNP.setScale(scale)
		
		self.model.setCollideMask(BitMask32.allOff())
				
# 		self.modelCollider = None
# 		self.modelRay = None
		self.wallHandler = CollisionHandlerPusher()
		self.floorHandler = CollisionHandlerGravity()
		self.floorHandler.setGravity(9.81+55)
		self.floorHandler.setMaxVelocity(100)
	
# 	def setFloorCollision(self, fromMask, intoMask):
# 		# the player's ray collider for ground collision detection
# 		raygeometry = CollisionRay(0, 0, 1, 0, 0, -1)
# 		self.modelRay = self.modelNP.attachNewNode(CollisionNode(self.name + 'Ray'))
# 		self.modelRay.node().addSolid(raygeometry)
# 		self.modelRay.node().setFromCollideMask(fromMask)
# 		self.modelRay.node().setIntoCollideMask(intoMask)
# 		self.floorHandler.addCollider(self.modelRay, self.modelNP)
# 		# ...then add the player collide sphere and the wall handler
# 		self.base.cTrav.addCollider(self.modelRay, self.floorHandler)	
# 		
# 	def setWallCollision(self, fromMask, intoMask):
# 		self.modelCollider.node().setFromCollideMask(fromMask)
# 		self.modelCollider.node().setIntoCollideMask(intoMask)
# 		self.wallHandler.addCollider(self.modelCollider, self.modelNP)
# 		
# 		self.base.cTrav.addCollider(self.modelCollider, self.wallHandler)
		
	def setTerrainCollision(self, wallPath, floorPath, wallMask, floorMask):
		self.floorcollider = self.model.find(floorPath)
		self.wallcollider  = self.model.find(wallPath)
		
# 		if not self.floorcollider.is_empty:
		self.floorcollider.node().setFromCollideMask(BitMask32.allOff())
		self.floorcollider.node().setIntoCollideMask(floorMask)
			
# 		if not self.wallcollider.is_empty:
		self.wallcollider.node().setFromCollideMask(BitMask32.allOff())
		self.wallcollider.node().setIntoCollideMask(wallMask)
		
	def getFloorHandler(self):
		return self.floorHandler
	
	def getPos(self):
		return self.modelNP.getPos()
	
	def setModelPos(self,pos):
		self.model.setPos(pos)
		
	def setNodePathPos(self,pos):
		self.modelNP.setPos(pos)
	
	def getScale(self):
		return self.model.getScale()
	
	def setScale(self,scale):
		self.model.setScale(scale)
	
	def setPosInterval(self, time, startPos, finalPos, onAxis = True):
		if (onAxis): return self.modelNP.posInterval(time,finalPos,startPos)
		else: return self.model.posInterval(time,finalPos,startPos)
	
	def setHprInterval(self, time, startAngle, finalAngle, onAxis = True):
		if (onAxis): return self.modelNP.hprInterval(time,finalAngle,startAngle)
		else: return self.model.hprInterval(time,finalAngle,startAngle)
	
	def getModel(self):
		return self.model
	
	def getNodePath(self):
		return self.modelNP