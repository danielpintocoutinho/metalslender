from pandac.PandaModules import BitMask32, Vec3

from scene_obj import SceneObject
from collision import CollisionMask as Mask

class Room(SceneObject):

	def __init__(self, base, name, model, scene, pos=Vec3(0,0,0), scale=1.0):
		self.root = scene.attachNewNode(name)
		
		self.model = base.loader.loadModel(model)
		self.model.reparentTo(self.root)
		
		self.root.setPos(pos)
		self.root.setScale(scale)
		
# 		self.root.setCollideMask(BitMask32.allOff())
		
		#TODO: Adjust ramp collision
		#TODO: Load room objects and triggers
		self.setCollision("**/*walls*", Mask.WALL)
		self.setCollision("**/*floor*", Mask.FLOOR)
		
	def setCollision(self, pattern, intoMask):
		for np in self.model.findAllMatches(pattern): 
			np.node().setIntoCollideMask(intoMask)