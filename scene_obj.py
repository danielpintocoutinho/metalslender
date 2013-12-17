from pandac.PandaModules import CollisionHandlerGravity, CollisionHandlerPusher, \
	CollisionNode, CollisionSphere, CollisionRay, Vec3

from collision import CollisionMask as Mask

class SceneObject:

	def __init__(self, base, name, model, scene, pos=Vec3(0,0,0), scale=1.0):

		self.root = scene.attachNewNode(name)

# 				self.modelBody = self.model.attachNewNode(CollisionNode(name + 'col'))
	
		self.collSol = self.root.attachNewNode(CollisionNode(name + 'Collision.Solid'))
		self.collRay = self.root.attachNewNode(CollisionNode(name + 'Collision.Ray'))
		
		self.wallHandler  = CollisionHandlerPusher()
		self.floorHandler = CollisionHandlerGravity()
		#TODO: Adjust gravity and max velocity
		self.floorHandler.setGravity(9.81+80)
# 		self.floorHandler.setMaxVelocity(1000)
		#BUG: The player cannot walk through a wall, but he may run through it!
		
		self.floorHandler.addCollider(self.collRay, self.root)
		base.cTrav.addCollider(self.collRay, self.floorHandler)
		
		self.wallHandler.addCollider(self.collSol, self.root)
		base.cTrav.addCollider(self.collSol, self.wallHandler)
			
	def addCollisionRay(self, ray = CollisionRay(0, 0, 1, 0, 0, -1)):
		self.collRay.node().addSolid(ray)
		
	def addCollisionSolid(self, solid = CollisionSphere(0, 0, 0, 1)):
		self.collSol.node().addSolid(solid)
	
	def setFloorCollision(self, fromMask=Mask.NONE, intoMask=Mask.NONE):
		self.collRay.node().setFromCollideMask(fromMask)
		self.collRay.node().setIntoCollideMask(intoMask)
		
	def setWallCollision(self, fromMask=Mask.NONE, intoMask=Mask.NONE):
		self.collSol.node().setFromCollideMask(fromMask)
		self.collSol.node().setIntoCollideMask(intoMask)
	
	def getNodePath(self):
		return self.root
	
	def __del__(self):
		self.collSol.removeNode()
		self.collRay.removeNode()
		self.root.removeNode()
		
