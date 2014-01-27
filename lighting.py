from panda3d.core import PerspectiveLens, Spotlight, Vec4

#TODO: Think about it: should all task management be setup in MetalSlender class?
class Flashlight:

	POWER_MIN  = 0.06
	POWER_DRAIN_RATE = -1/240.0
	POWER_GAIN_RATE  =  1/480.0
	
	EXPONENET = 40 
	
	COLOR = Vec4(1.0, 1.0, 0.9, 1)
	
	ATT_CONST = 0
	ATT_LIN   = 0.3
	ATT_QUAD  = 0.05
	
	def __init__(self, name, owner, scene, pos, fov=60, near=0.01, far=100, resol=(1920, 1080)):
		self.owner = owner
		self.scene = scene
		
		self.last      = 0.0
		self.power     = 1.0
		self.on        = True
		self.powerrate = Flashlight.POWER_DRAIN_RATE 

		#TODO: Change lens parameters for a unique 'lens' parameter
		lens = PerspectiveLens()
		lens.setFov(fov)
		lens.setNearFar(near, far)
		lens.setFilmSize(resol[0], resol[1])

		self.light = Spotlight(name + '/wide')
		self.light.setLens(lens)
		#TODO: Shadows don't work well anymore
		#self.light.setShadowCaster(True, resol[0], resol[1])
		self.light.setColor(Flashlight.COLOR)
		self.light.setExponent(40)
		
		self.nodepath = owner.cam.attachNewNode(self.light)
		self.nodepath.setPos(pos)
		self.nodepath.setHpr((5,5,0))
		
		self.scene.setLight(self.nodepath)

	def __del__(self):
		self.nodepath.removeNode()

	def toggle(self):
		self.on = not self.on
		if self.on:
			self.scene.setLight(self.nodepath)
			self.powerrate = Flashlight.POWER_DRAIN_RATE
		else:
			self.scene.clearLight(self.nodepath)
			self.powerrate = Flashlight.POWER_GAIN_RATE

	def updatePower(self, task):
		elapsed = task.time - self.last
		
		self.last = task.time
		self.power = max(Flashlight.POWER_MIN, min(1.0, self.power + elapsed * self.powerrate))
		
		self.light.setAttenuation((Flashlight.ATT_CONST, Flashlight.ATT_LIN, Flashlight.ATT_QUAD / self.power))

		return task.cont
	
	def getNodePath(self):
		return self.nodepath
	
	def setHpr(self, vec):
		self.nodepath.setHpr(vec)

	def isOn(self):
		return self.on
