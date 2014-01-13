from panda3d.core import BitMask32, CollisionRay, CollisionSphere, Vec3

from hooded import *
from scene_obj import SceneObject
from collision import CollisionMask as Mask

class Enemy(SceneObject):
	
	HEIGHT = 1.8
	
	SIGHT_NEAR = HEIGHT/18
	SIGHT_FAR  = 100
	
	BODY_SOLID = CollisionSphere(0, 0, HEIGHT / 2, HEIGHT / 9)
	FEET_SOLID = CollisionRay   (0, 0, HEIGHT * 9, 0, 0, -1)
# 	BODY_SOLID = CollisionSphere(0, 0, 0, HEIGHT / 9)
# 	FEET_SOLID = CollisionRay   (0, 0, 0, 0, 0, -1)

	def __init__(self, base, scene, name, route=[], pos=Vec3(0,0,0), scale=1.0):
		SceneObject.__init__(self, base, scene, name, pos, scale)
		
		self.seeker = Actor("assets/chicken/vulto-pedro")
		#self.seeker = Actor("models/ralph",{"run":"models/ralph-run", "walk":"models/ralph-walk"})
# 		self.seeker.setCollideMask(BitMask32.allOff())
# 		self.pos = pos
# 		self.pos.z += 10
# 		self.seeker.setPos(self.pos)
		self.seeker.reparentTo(self.root)
		#self.seeker.setScale(6)
		
		self.setBodySolid(Enemy.BODY_SOLID)
		self.setFeetSolid(Enemy.FEET_SOLID)
	
		self.setBodyCollision (fromMask=Mask.WALL  )
		self.setFeetCollision (fromMask=Mask.FLOOR )

# 		self.hooded = Hooded("seeker", self.seeker, 60, 2, 2)
# 		self.hooded.setPatrolPos(route)
		
	def __del__(self):
		self.seeker.removeNode()
		self.hooded = None
		self.model.removeNode()		

	def getHooded(self):
		return self.hooded

	def update(self):
		pass
# 		return self.hooded.update()

	def addDynamicObjects(self, objects):
		for o in objects:
			self.hooded.addDynamicObject(o)

	def hear(self, noisePos):
		self.hooded.hear(noisePos)

	def start(self):
		pass
# 		self.hooded.start()

	def stop(self):
		self.hooded.stop()