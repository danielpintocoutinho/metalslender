from panda3d.core import PerspectiveLens, Spotlight, Vec4
from panda3d.core import *

#TODO: Think about it: should all task management be setup in MetalSlender class?
class Flashlight:

	POWER_MIN  = 0.06
	POWER_DRAIN_RATE = -1/240.0
	POWER_GAIN_RATE  =  1/480.0
	
	ATT_CONST = 2
	ATT_LIN   = 0.04
	ATT_QUAD  = 0.004
	
	def __init__(self, name, owner, scene, pos, color = Vec4(1.0, 1.0, 0.9, 1), fov=60, near=0.01, far=100, resol=(1920,1080)):
		self.owner = owner
		self.scene = scene
		self.color = color
		
		self.last      = 0.0
		self.power     = 1.0
		self.on        = True
		self.powerrate = Flashlight.POWER_DRAIN_RATE 
		
		self.nodepath = owner.cam.attachNewNode(name)
		self.nodepath.setPos(pos)
		self.nodepath.setHpr((5,5,0))

		lens1 = PerspectiveLens()
# 		lens2 = PerspectiveLens()
		
		lens1.setFov(60)
# 		lens2.setFov(30)
		
		lens1.setNearFar(near, far)
# 		lens2.setNearFar(near, far)

# 		lens1.setFilmSize(resol[0], resol[1])

		self.light1 = Spotlight(name + '/wide')
# 		self.light2 = Spotlight(name + '/narrow')
		
# 		self.light1.setShadowCaster(True, resol[0], resol[1], 1)
# 		self.light1.setShadowCaster(True)
# 		self.light2.setShadowCaster(False)
		
		self.light1.setColor(color)
# 		self.light2.setColor(color)
		
		self.light1.setExponent(40)
# 		self.light2.setExponent(120)
		
		self.light1.setLens(lens1)
# 		self.light2.setLens(lens2)
		
		self.node1 = self.nodepath.attachNewNode(self.light1)
# 		self.node2 = self.nodepath.attachNewNode(self.light2)
		
# 		self.light2.setAttenuation((6 * Flashlight.ATT_CONST, 6 * Flashlight.ATT_LIN, 6 * Flashlight.ATT_QUAD))

		self.scene.setLight(self.node1)
# 		self.scene.setLight(self.node2)

	def toggle(self):
		self.on = not self.on
		if self.on:
			self.scene.setLight(self.node1)
# 			self.scene.setLight(self.node2)
			self.powerrate = Flashlight.POWER_DRAIN_RATE
		else:
			self.scene.clearLight(self.node1)
# 			self.scene.clearLight(self.node2)
			self.powerrate = Flashlight.POWER_GAIN_RATE

	def updatePower(self, task):
		elapsed = task.time - self.last
		
		self.last = task.time
		self.power = max(Flashlight.POWER_MIN, min(1.0, self.power + elapsed * self.powerrate))
		
		self.light1.setAttenuation((Flashlight.ATT_CONST, Flashlight.ATT_LIN, Flashlight.ATT_QUAD / self.power))

		return task.cont
	
	def getNodePath(self):
		return self.nodepath
	
	def setHpr(self, vec):
		self.node1.setHpr(vec)

	def isOn(self):
		return self.on
