from panda3d.core import BitMask32, CullFaceAttrib, DirectionalLight, Material, NodePath, PerspectiveLens, PointLight, Spotlight, TransparencyAttrib, Vec3, Vec4
from direct.actor.Actor import Actor

from constants import *
from scene_obj import SceneObject
from collision import CollisionMask as Mask
from enemy import Enemy

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
# 		del self.lights [:]
			
	#TODO: Find out what is missing in the scenario
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
		self.doors  = self.model.findAllMatches('**/Door*')
 		base.doors += self.doors

	def setupKeys(self, base):
		for np in self.model.findAllMatches('**/Key*'):
	 		base.keys.append(np)
	 		
	def setupTrees(self):
		for tree in self.model.findAllMatches('**/=Tree'):
			tree.setTwoSided(True)
			tree.setBillboardAxis()
			tree.setTransparency(TransparencyAttrib.MAlpha)
			
	def setupCollision(self):
		#TODO: Load room objects and triggers
		self.setCollision("**/=Barrier", Mask.WALL | Mask.FLOOR)
		self.setCollision("**/=Door"   , Mask.WALL)
		self.setCollision("**/=Wall"   , Mask.WALL)
		self.setCollision("**/=Floor"  , Mask.FLOOR)
		self.setCollision("**/*walls*" , Mask.WALL)
		self.setCollision("**/*floor*" , Mask.FLOOR)
		self.setCollision("**/*escada*", Mask.FLOOR)
		
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