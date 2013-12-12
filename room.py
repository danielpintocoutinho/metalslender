from pandac.PandaModules import BitMask32, DirectionalLight, NodePath, PerspectiveLens, PointLight, Spotlight, Vec3, Vec4

from scene_obj import SceneObject
from collision import CollisionMask as Mask

class Room(SceneObject):

	def __init__(self, base, name, model, scene, pos=Vec3(0,0,0), scale=1.0):
		self.root = scene.attachNewNode(name)
		
		self.model = base.loader.loadModel(model)
		self.model.reparentTo(self.root)
		
		self.root.setPos(pos)
		self.root.setScale(scale)
		
		self.setupLightSources(scene)
		
		#TODO: Adjust ramp collision
		#TODO: Load room objects and triggers
		self.setCollision("**/*walls*", Mask.WALL)
		self.setCollision("**/*floor*", Mask.FLOOR)
		
	def setupLightSources(self, scene):
		self.lights = []
		
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
			
			if np.getTag('Hide'):
				np.removeNode()
		
	def setCollision(self, pattern, intoMask):
		for np in self.model.findAllMatches(pattern): 
			np.node().setIntoCollideMask(intoMask)