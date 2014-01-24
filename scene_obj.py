from pandac.PandaModules import CollisionHandlerPhysical, CollisionNode, Vec3

from collision import CollisionMask as Mask
from direct.showbase.DirectObject import DirectObject

class SceneObject(DirectObject):

	def __init__(self, base, scene, name, pos=Vec3(0,0,0), hpr=Vec3(0, 0, 0), scale=1.0):

		self.base  = base
		self.scene = scene

		self.root = scene.attachNewNode(name)
		self.root.setPos(pos)
		self.root.setHpr(hpr)
		self.root.setScale(scale)
		
		self.collisionNodes = {}
	
	def __del__(self):
		self.root.removeNode()
		
	def getNodePath(self):
		return self.root
		
	def addCollisionGroup(self, key, solids, handler, masks):
		self.addCollisionNode(key)
		self.addCollisionSolids(key, solids)
		self.addCollisionHandler(key, handler)
		self.setCollisionMasks(key, masks[0], masks[1])
		
	def addCollisionNode(self, key, name = None):
		if name is None:
			name = str(key)
		if key in self.collisionNodes:
			del self.collisionNodes[key]
		self.collisionNodes[key] = (self.root.attachNewNode(CollisionNode(name)), [])
	
	def getCollisionNode(self, key):
		return self.collisionNodes[key][0]
	
	def getCollisionKeys(self):
		return self.collisionNodes.keys()
	
	def delCollisionNode(self, key):
		del self.collisionNodes[key][0]
		
	def addCollisionSolid(self, key, solid):
		self.addCollisionSolids(key, [solid])
		
	def addCollisionSolids(self, key, solids):
		for s in solids:
			self.getCollisionNode(key).node().addSolid(s)
			
	def getCollisionSolid(self, key, index):
		return self.getCollisionSolids()[index]
		
	def getCollisionSolids(self, key, solid):
		return self.getCollisionNode(key).node().getSolids()
	
	def setCollisionSolid(self, key, solid):
		self.setCollisionSolids(key, [solid])
	
	def setCollisionSolids(self, key, solids):
		self.clearCollisionSolids(key)
		self.addCollisionSolids(key, solids)
	
	def delCollisionSolid(self, key, index):
		self.getCollisionNode(key).node().removeSolid(index)
		
	def clearCollisionSolids(self, key):
		self.getCollisionNode(key).node().clearSolids()
	
	def addCollisionHandler(self, key, handler):
		self.collisionNodes[key][1].append(handler)
		if isinstance(handler, CollisionHandlerPhysical):
			handler.addCollider(self.getCollisionNode(key), self.root)
		self.base.cTrav.addCollider(self.getCollisionNode(key), handler)
		
	def getCollisionHandler(self, key, index=0):
		return self.getCollisionHandlers(key)[index]
		
	def getCollisionHandlers(self, key):
		return self.collisionNodes[key][1]
	
	def getCollisionMasks(self, key):
		fromMask = self.collisionNodes[key].node().getFromCollideMask()
		intoMask = self.collisionNodes[key].node().getIntoCollideMask()
		return (fromMask, intoMask)
	
	def setCollisionMasks(self, key, fromMask=Mask.NONE, intoMask=Mask.NONE):
		self.getCollisionNode(key).node().setFromCollideMask(fromMask)
		self.getCollisionNode(key).node().setIntoCollideMask(intoMask)