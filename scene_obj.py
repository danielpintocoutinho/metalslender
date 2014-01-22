from pandac.PandaModules import CollisionHandlerEvent, CollisionHandlerGravity, PhysicsCollisionHandler, CollisionHandlerPusher, \
	CollisionNode, CollisionSegment, CollisionSphere, CollisionRay, Vec3

from collision import CollisionMask as Mask
from direct.showbase.DirectObject import DirectObject

#TODO: Definition of collision solids takes a lot of code repetition
class SceneObject(DirectObject):
	
	AURA_SOLID_SUFIX = 'AuraSolid'
	BODY_SOLID_SUFIX = 'BodySolid'
	FEET_SOLID_SUFIX = 'FeetSolid'
	JUMP_SOLID_SUFIX = 'JumpSolid'
	HAND_SOLID_SUFIX = 'HandSolid'

	def __init__(self, base, scene, name, pos=Vec3(0,0,0), scale=1.0):

		self.base  = base
		self.scene = scene

		self.root = scene.attachNewNode(name)
		self.root.setPos(pos)
		self.root.setScale(scale)
	
		self.auraCollider = self.root.attachNewNode(CollisionNode(name + SceneObject.AURA_SOLID_SUFIX))
		self.bodyCollider = self.root.attachNewNode(CollisionNode(name + SceneObject.BODY_SOLID_SUFIX))
		self.feetCollider = self.root.attachNewNode(CollisionNode(name + SceneObject.FEET_SOLID_SUFIX))
		self.jumpCollider = self.root.attachNewNode(CollisionNode(name + SceneObject.JUMP_SOLID_SUFIX))
		self.handCollider = self.root.attachNewNode(CollisionNode(name + SceneObject.HAND_SOLID_SUFIX))
		
		self.auraHandler = CollisionHandlerEvent()
		self.bodyHandler = CollisionHandlerPusher()
		self.feetHandler = CollisionHandlerGravity()
		self.jumpHandler = CollisionHandlerEvent()
		self.handHandler = CollisionHandlerEvent()

		self.feetHandler.setGravity(9.81)
		
		self.bodyHandler.addCollider(self.bodyCollider, self.root)
		self.feetHandler.addCollider(self.feetCollider, self.root)
	
	def __del__(self):
		self.root.removeNode()
		
	def setAuraSolid(self, solid = CollisionSphere(0, 0, 0, 1)):
		self.auraCollider.node().clearSolids()
		self.auraCollider.node().addSolid(solid)
					
	def setBodySolid(self, solid = CollisionSphere(0, 0, 0, 1)):
		self.bodyCollider.node().clearSolids()
		self.bodyCollider.node().addSolid(solid)
		
	def setFeetSolid(self, solid = CollisionRay(0, 0, 1, 0, 0, -1)):
		self.feetCollider.node().clearSolids()
		self.feetCollider.node().addSolid(solid)
			
	def setJumpSolid(self, solid = CollisionSegment(0, 0, 1, 0, 0, -1)):
		self.jumpCollider.node().clearSolids()
		self.jumpCollider.node().addSolid(solid)
		
	def setHandSolid(self, solid = CollisionSegment(0, 0, 0, 0, 1, 0)):
		self.handCollider.node().clearSolids()
		self.handCollider.node().addSolid(solid)
		
	def setAuraCollision(self, fromMask=Mask.NONE, intoMask=Mask.NONE):
		self.auraCollider.node().setFromCollideMask(fromMask)
		self.auraCollider.node().setIntoCollideMask(intoMask)
		
		if fromMask != Mask.NONE:
			self.base.cTrav.addCollider(self.auraCollider, self.auraHandler)
		
	def setBodyCollision(self, fromMask=Mask.NONE, intoMask=Mask.NONE):
		self.bodyCollider.node().setFromCollideMask(fromMask)
		self.bodyCollider.node().setIntoCollideMask(intoMask)
		
		if fromMask != Mask.NONE:
			self.base.cTrav.addCollider(self.bodyCollider, self.bodyHandler)
	
	def setFeetCollision(self, fromMask=Mask.NONE, intoMask=Mask.NONE):
		self.feetCollider.node().setFromCollideMask(fromMask)
		self.feetCollider.node().setIntoCollideMask(intoMask)
		
		if fromMask != Mask.NONE:
			self.base.cTrav.addCollider(self.feetCollider, self.feetHandler)
		
	def setJumpCollision(self, fromMask=Mask.NONE, intoMask=Mask.NONE):
		self.jumpCollider.node().setFromCollideMask(fromMask)
		self.jumpCollider.node().setIntoCollideMask(intoMask)
		
		if fromMask != Mask.NONE:
			self.base.cTrav.addCollider(self.jumpCollider, self.jumpHandler)
				
	def setHandCollision(self, fromMask=Mask.NONE, intoMask=Mask.NONE):
		self.handCollider.node().setFromCollideMask(fromMask)
		self.handCollider.node().setIntoCollideMask(intoMask)
		
		if fromMask != Mask.NONE:
			self.base.cTrav.addCollider(self.handCollider, self.handHandler)
	
	def getNodePath(self):
		return self.root