from panda3d.core import BitMask32, CollisionHandlerGravity, CollisionHandlerPusher, CollisionRay, CollisionSphere, Vec3
from direct.actor.Actor import Actor

from constants import *
from hooded import *
from scene_obj import SceneObject
from collision import CollisionMask as Mask

class Enemy(SceneObject):
	
	SIGHT_NEAR = Hooded.HEIGHT/18
	SIGHT_FAR  = 100
	
	FEET_NODE = 'FeetNode'
	BODY_NODE = 'BodyNode'
	
	BODY_SOLID = CollisionSphere (0, 0, Hooded.HEIGHT / 2, Hooded.HEIGHT / 9)
	FEET_SOLID = CollisionRay    (0, 0, Hooded.HEIGHT / 2, 0, 0, -1)
	
	GRAVITY_FACTOR =  1.0 / 6.0

	actor = None

	def __init__(self, base, scene, np):
		SceneObject.__init__(self, base, scene, np.getName(), np.getPos(), np.getHpr(), np.getScale())
		
		#TODO: fix animation in blender
		if Enemy.actor is None:
			Enemy.actor = Actor(EGG_HOODED, {})#{'Hover' : EGG_HOODED + '-Hover'})
			Enemy.actor.setPos(0, 0, 0)
			Enemy.actor.reparentTo(self.root)
			Enemy.actor.loop('Hover')
			
		patrol = [scene.find('**/Waypoint.' + w) for w in np.getTag('Patrol').split(',')]
		
		Enemy.actor.instanceTo(self.root)
		
		self.hooded = Hooded(np.getName() + 'Hooded', self.root, patrol, 60, 4, 4)
		for o in scene.findAllMatches('**/=Door'):
			self.hooded.addDynamicObject(o)

		base.AIworld.addAiChar(self.hooded)
		
		self.addCollisionGroup(Enemy.FEET_NODE, [Enemy.FEET_SOLID], CollisionHandlerGravity(), (Mask.SCENE, Mask.NONE))
		self.addCollisionGroup(Enemy.BODY_NODE, [Enemy.BODY_SOLID], CollisionHandlerPusher (), (Mask.SCENE, Mask.NONE))
		
		self.getCollisionHandler(Enemy.FEET_NODE).setGravity(self.base.GRAVITY * Enemy.GRAVITY_FACTOR)

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