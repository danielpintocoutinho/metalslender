from panda3d.core import BitMask32, CollisionRay, CollisionSphere, Vec3
from direct.actor.Actor import Actor

from constants import *
from hooded import *
from scene_obj import SceneObject
from collision import CollisionMask as Mask

class Enemy(SceneObject):
	
	SIGHT_NEAR = Hooded.HEIGHT/18
	SIGHT_FAR  = 100
	
	BODY_SOLID = CollisionSphere(0, 0, Hooded.HEIGHT / 2, Hooded.HEIGHT / 9)
	FEET_SOLID = CollisionRay    (0, 0,  Hooded.HEIGHT / 2, 0, 0, -1)

	actor = None

	def __init__(self, base, scene, np):
		SceneObject.__init__(self, base, scene, np.getName(), np.getPos(), np.getScale())
		
		if Enemy.actor is None:
			Enemy.actor = Actor(EGG_HOODED, {'Hover' : 'assets/chicken/vulto-pedro-Hover'})
			Enemy.actor.setPos(0, 0, 0)
			Enemy.actor.reparentTo(self.root)
			Enemy.actor.loop('Hover')
			
		patrol = [scene.find('**/Waypoint.' + w) for w in np.getTag('Patrol').split(',')]
		
		Enemy.actor.instanceTo(self.root)
		
		self.hooded = Hooded(np.getName() + 'Hooded', self.root, patrol, 60, 5, 2)
		for o in scene.findAllMatches('**/=Door'):
			self.hooded.addDynamicObject(o)

		base.AIworld.addAiChar(self.hooded)
		
		self.setBodySolid(Enemy.BODY_SOLID)
		self.setFeetSolid(Enemy.FEET_SOLID)
	
		self.setBodyCollision (fromMask=Mask.WALL  )
		self.setFeetCollision (fromMask=Mask.FLOOR )	

	def getHooded(self):
		return self.hooded
	
	def hear(self, noisePos):
		self.hooded.hear(noisePos)

	def update(self):
		return self.hooded.update()

	def start(self):
		self.hooded.start()

	def stop(self):
		self.hooded.stop()

# 	def update(self):
# 		pass
# 
# 	def start(self):
# 		pass
# 
# 	def stop(self):
# 		pass