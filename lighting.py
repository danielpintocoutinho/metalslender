from panda3d.core import *
from direct.showbase.DirectObject import DirectObject

from math import sin, pi

spotlight1s = {}
alight1 = None

POWER_MIN  = 0.03
POWER_RATE = -1/120.0

class Flashlight(DirectObject):
	def __init__(self, name, owner, color = Vec4(1.0, 1.0, 0.9, 1), fov =	60,	near = 0.01, far = 100):
		self.color = color
		self.power = 1.0
		self.last  = 0.0
		self.on    = True
		self.owner = owner

		self.node1 = owner.modelNP.attachNewNode(Spotlight(name + 'wide'))
		self.node1.reparentTo(owner.cam)
		self.node1.setPos((5, 2, -5))
		self.node1.setHpr((5,5,0))

		lens1 = PerspectiveLens()
		lens1.setFov(40)
		lens1.setNearFar(near, far)

		self.light1 = self.node1.node()
		self.light1.setShadowCaster(True)
		self.light1.setColor(color)
		self.light1.setExponent(40)
		self.light1.setLens(lens1)
		self.light1.setAttenuation((0.5,0.001,0.0001))

		render.setLight(self.node1)

		self.accept('l', self.toggle)

		taskMgr.add(self.updatePower, 'flashlight1/update')

	def toggle(self):
		self.on = not self.on
		if self.on:
			render.setLight(self.node1)
		else:
			render.clearLight(self.node1)

	def updatePower(self, task):
		elapsed = task.time - self.last
		self.last = task.time

		self.power = max(POWER_MIN, self.power + elapsed * POWER_RATE * self.on)
		self.light1.setAttenuation((0.5, 0.001, 0.0001 / self.power))

		return task.cont
