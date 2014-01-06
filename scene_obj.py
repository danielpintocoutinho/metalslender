from pandac.PandaModules import CollisionHandlerEvent, CollisionHandlerGravity, PhysicsCollisionHandler, CollisionHandlerPusher, \
	CollisionNode, CollisionSegment, CollisionSphere, CollisionRay, Vec3

from collision import CollisionMask as Mask
from direct.showbase.DirectObject import DirectObject

class SceneObject(DirectObject):
	
	AURA_SOLID_SUFIX = 'AuraSolid'
	BODY_SOLID_SUFIX = 'BodySolid'
	FEET_SOLID_SUFIX = 'FeetSolid'

	def __init__(self, base, name, scene, pos=Vec3(0,0,0), scale=1.0):

		self.root = scene.attachNewNode(name)
		self.root.setPos(pos)
		self.root.setScale(scale)
	
		self.auraSolid = self.root.attachNewNode(CollisionNode(name + SceneObject.AURA_SOLID_SUFIX))
		self.bodySolid = self.root.attachNewNode(CollisionNode(name + SceneObject.BODY_SOLID_SUFIX))
		self.feetSolid = self.root.attachNewNode(CollisionNode(name + SceneObject.FEET_SOLID_SUFIX))
		
		self.auraHandler = CollisionHandlerEvent()
		#TODO: If this guy is an actor
		#self.bodyHandler  = PhysicsCollisionHandler()
		self.bodyHandler = CollisionHandlerPusher()
		self.feetHandler = CollisionHandlerGravity()
		
# 		self.auraHandler.addInPattern('into-%in')
# 		self.auraHandler.addAgainPattern('%fn-again-%in')
# 		self.auraHandler.addOutPattern('out-%in')

		self.feetHandler.setGravity(9.81)
# 		self.keepHandler.setGravity(9.81)
# 		self.feetHandler.setMaxVelocity(1000)
		
		base.cTrav.addCollider(self.auraSolid, self.auraHandler)
		base.cTrav.addCollider(self.bodySolid, self.bodyHandler)
		base.cTrav.addCollider(self.feetSolid, self.feetHandler)
		
		self.bodyHandler.addCollider(self.bodySolid, self.root)
		self.feetHandler.addCollider(self.feetSolid, self.root)
	
	def __del__(self):
#TODO: Verify in Panda documentation that upon removing the root node, all its children are also removed
# 		self.bodySolid.removeNode()
# 		self.feetSolid.removeNode()
# 		self.keepSolid.removeNode()
		self.root.removeNode()
		
	def setAuraSolid(self, solid = CollisionSphere(0, 0, 0, 1)):
		self.auraSolid.node().clearSolids()
		self.auraSolid.node().addSolid(solid)
					
	def setBodySolid(self, solid = CollisionSphere(0, 0, 0, 1)):
		self.bodySolid.node().clearSolids()
		self.bodySolid.node().addSolid(solid)
		
	def setFeetSolid(self, solid = CollisionRay(0, 0, 1, 0, 0, -1)):
		self.feetSolid.node().clearSolids()
		self.feetSolid.node().addSolid(solid)
		
	def setAuraCollision(self, fromMask=Mask.NONE, intoMask=Mask.NONE):
		self.auraSolid.node().setFromCollideMask(fromMask)
		self.auraSolid.node().setIntoCollideMask(intoMask)
		
	def setBodyCollision(self, fromMask=Mask.NONE, intoMask=Mask.NONE):
		self.bodySolid.node().setFromCollideMask(fromMask)
		self.bodySolid.node().setIntoCollideMask(intoMask)
	
	def setFeetCollision(self, fromMask=Mask.NONE, intoMask=Mask.NONE):
		self.feetSolid.node().setFromCollideMask(fromMask)
		self.feetSolid.node().setIntoCollideMask(intoMask)
	
	def getNodePath(self):
		return self.root