from pandac.PandaModules import CollisionHandlerEvent, CollisionHandlerGravity, PhysicsCollisionHandler, CollisionHandlerPusher, \
	CollisionNode, CollisionSegment, CollisionSphere, CollisionRay, Vec3

from collision import CollisionMask as Mask
from direct.showbase.DirectObject import DirectObject

class SceneObject(DirectObject):
	
	AURA_SOLID_SUFIX = 'AuraSolid'
	BODY_SOLID_SUFIX = 'BodySolid'
	FEET_SOLID_SUFIX = 'FeetSolid'
	JUMP_SOLID_SUFIX = 'JumpSolid'

	def __init__(self, base, name, scene, pos=Vec3(0,0,0), scale=1.0):

		self.root = scene.attachNewNode(name)
		self.root.setPos(pos)
		self.root.setScale(scale)
	
		self.auraColNode = self.root.attachNewNode(CollisionNode(name + SceneObject.AURA_SOLID_SUFIX))
		self.bodyColNode = self.root.attachNewNode(CollisionNode(name + SceneObject.BODY_SOLID_SUFIX))
		self.feetColNode = self.root.attachNewNode(CollisionNode(name + SceneObject.FEET_SOLID_SUFIX))
		self.jumpColNode = self.root.attachNewNode(CollisionNode(name + SceneObject.JUMP_SOLID_SUFIX))
		
		self.auraColHandler = CollisionHandlerEvent()
		#TODO: If this guy is an actor
		#self.bodyColHandler  = PhysicsCollisionHandler()
		self.bodyColHandler = CollisionHandlerPusher()
		self.feetColHandler = CollisionHandlerGravity()
		self.jumpColHandler = CollisionHandlerEvent()
		
# 		self.auraColHandler.addInPattern('into-%in')
# 		self.auraColHandler.addAgainPattern('%fn-again-%in')
# 		self.auraColHandler.addOutPattern('out-%in')

		self.feetColHandler.setGravity(9.81)
# 		self.keepHandler.setGravity(9.81)
# 		self.feetColHandler.setMaxVelocity(1000)
		
		base.cTrav.addCollider(self.auraColNode, self.auraColHandler)
		base.cTrav.addCollider(self.bodyColNode, self.bodyColHandler)
		base.cTrav.addCollider(self.feetColNode, self.feetColHandler)
		base.cTrav.addCollider(self.jumpColNode, self.jumpColHandler)
		
		self.bodyColHandler.addCollider(self.bodyColNode, self.root)
		self.feetColHandler.addCollider(self.feetColNode, self.root)
	
	def __del__(self):
#TODO: Verify in Panda documentation that upon removing the root node, all its children are also removed
# 		self.bodyColNode.removeNode()
# 		self.feetColNode.removeNode()
# 		self.keepSolid.removeNode()
		self.root.removeNode()
		
	def setAuraSolid(self, solid = CollisionSphere(0, 0, 0, 1)):
		self.auraColNode.node().clearSolids()
		self.auraColNode.node().addSolid(solid)
					
	def setBodySolid(self, solid = CollisionSphere(0, 0, 0, 1)):
		self.bodyColNode.node().clearSolids()
		self.bodyColNode.node().addSolid(solid)
		
	def setFeetSolid(self, solid = CollisionRay(0, 0, 1, 0, 0, -1)):
		self.feetColNode.node().clearSolids()
		self.feetColNode.node().addSolid(solid)
			
	def setJumpSolid(self, solid = CollisionSegment(0, 0, 1, 0, 0, -1)):
		self.jumpColNode.node().clearSolids()
		self.jumpColNode.node().addSolid(solid)
		
	def setAuraCollision(self, fromMask=Mask.NONE, intoMask=Mask.NONE):
		self.auraColNode.node().setFromCollideMask(fromMask)
		self.auraColNode.node().setIntoCollideMask(intoMask)
		
	def setBodyCollision(self, fromMask=Mask.NONE, intoMask=Mask.NONE):
		self.bodyColNode.node().setFromCollideMask(fromMask)
		self.bodyColNode.node().setIntoCollideMask(intoMask)
	
	def setFeetCollision(self, fromMask=Mask.NONE, intoMask=Mask.NONE):
		self.feetColNode.node().setFromCollideMask(fromMask)
		self.feetColNode.node().setIntoCollideMask(intoMask)
		
	def setJumpCollision(self, fromMask=Mask.NONE, intoMask=Mask.NONE):
		self.jumpColNode.node().setFromCollideMask(fromMask)
		self.jumpColNode.node().setIntoCollideMask(intoMask)
	
	def getNodePath(self):
		return self.root