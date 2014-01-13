from panda3d.core import BitMask32, CullFaceAttrib, DirectionalLight, Material, NodePath, PerspectiveLens, PointLight, Spotlight, TransparencyAttrib, Vec3, Vec4
from direct.actor.Actor import Actor

from constants import *
from key import Key
from door import Door
from scene_obj import SceneObject
from collision import CollisionMask as Mask
from enemy import Enemy

#TODO: things instantiated inside setup*() functions may all be enclosed in classes likewise Key and Door
class Room(SceneObject):

	def __init__(self, base, name, model, scene, pos=Vec3(0,0,0), scale=1.0):
		self.root = scene.attachNewNode(name)
		
		self.model = base.loader.loadModel(model)
		self.model.reparentTo(self.root)

		self.model.setDepthOffset(1)
		self.model.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullClockwise))
		
		self.root.setPos(pos)
		self.root.setScale(scale)
		
		self.lights = []
		self.doors  = []
		self.keys   = []
		
		self.setupDoors(base)
		self.setupKeys(base)
		self.setupLightSources(scene)
		self.setupCollision()
		self.setupEnemies(base)
		self.setupGoal(base)
		self.setupTrees()
		
		for np in self.model.findAllMatches('**/=Hide'):
			np.hide()
			
		for np in self.model.findAllMatches('**/=Barrier'):
			np.hide()
			
	def __del__(self):
		self.root.removeNode()
		#TODO: A lot of secondary objects to delete, such as doors and keys
# 		del self.lights [:]
			
	def setupEnemies(self, base):
		for np in self.model.findAllMatches('**/=Patrol'):
			patrol = [self.model.find('**/Waypoint.' + w) for w in np.getTag('Patrol').split(',')]
			#TODO: AI commands commented
			actor = Actor(EGG_HOODED)
			actor.setPos(np.getPos())
			actor.reparentTo(self.root)
# 	 		base.enemies.append(Enemy(base, 'Hooded.' + str(len(base.enemies)), self.root, patrol, np.getPos()))
# 			base.AIworld.addAiChar(base.enemies[-1].getHooded())
# 			base.enemies[-1].addDynamicObjects(self.doors)

	def setupGoal(self, base):
		np = self.model.find('**/Goal')
		base.goal = np

	def setupDoors(self, base):
		for np in self.model.findAllMatches('**/=Door'):
			self.doors.append(Door(base, np))

	def setupKeys(self, base):
		for np in self.model.findAllMatches('**/=Key'):
	 		self.keys.append(Key(base, np))
	 		
	def setupTrees(self):
		for tree in self.model.findAllMatches('**/=Tree'):
			tree.setTwoSided(True)
			tree.setBillboardAxis()
			tree.setTransparency(TransparencyAttrib.MAlpha)
			
	def setupCollision(self):
		self.setCollision("**/=Barrier", Mask.WALL | Mask.FLOOR)
		self.setCollision("**/=Wall"   , Mask.WALL)
		self.setCollision("**/=Floor"  , Mask.FLOOR | Mask.HAND)
		
	def setupLightSources(self, scene):
		for np in self.model.findAllMatches('**/=Light'):
			if np.getTag('Light') == 'Point':
				light = PointLight('PointLight.%d' % (len(self.lights) + 1,))
			elif np.getTag('Light') == 'Spot':
				light = Spotlight('Spotlight.%d' % (len(self.lights) + 1,))
				
				fov = np.getTag('Fov')
				if fov:
					light.getLens().setFov(float(fov))
					
				nf = np.getTag('NearFar').split(',')
				if len(nf) > 1:
					light.getLens().setNearFar(float(nf[0]), float(nf[1]))
				
				exp = np.getTag('Exponent')
				if exp:
					light.setExponent(float(exp))
					
			elif np.getTag('Light') == 'Directional':
				light = DirectionalLight('DirectionalLight.%d' % (len(self.lights) + 1,))	
			
			materials = np.findAllMaterials()
			if len(materials) > 0:
				light.setColor(materials[0].getDiffuse())
			
			attenuation = np.getTag('Attenuation').split(',')
			if len(attenuation) > 0 and not isinstance(light, DirectionalLight):
				light.setAttenuation(tuple([float(a) for a in attenuation]))
				
			if np.getTag('Shadow'):
# 				self.model.setShaderAuto()
				light.setShadowCaster(True)
			
			self.lights.append(light)
			
			lightNP = self.model.attachNewNode(light)
			lightNP.setPos(np.getPos())
			lightNP.setHpr(np.getHpr())
# 			lightNP.setCompass()
			self.model.setLight(lightNP)
		
	def setCollision(self, pattern, intoMask):
		for np in self.model.findAllMatches(pattern): 
			np.node().setIntoCollideMask(intoMask)