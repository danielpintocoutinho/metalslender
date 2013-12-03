from panda3d.core import *
from direct.showbase.DirectObject import DirectObject

from math import sin, pi

spotlight1s = {}
alight1 = None

POWER_MIN  = 0.001
POWER_RATE = -1/7.0

class Flashlight(DirectObject):
	def __init__(self, name, source, color = Vec4(1.0, 1.0, 0.95, 1), fov =	60,	near = 0.01, far = 100):
		self.color = color
		self.power = 1.0
		self.last  = 0.0
		self.on    = True

		self.node1 = render.attachNewNode(Spotlight(name + 'wide'))
		self.node2 = render.attachNewNode(Spotlight(name + 'narr'))
		#self.node1.reparentTo(base.cam)
		#self.node1.setPos((5, 10, -5))
		self.node1.setPos(0, 10, 25)
		self.node2.setPos(0, 10, 25)
		#self.node2.setPos(0, 0, 50)
		self.node1.setHpr(-90, 0, 0)
		self.node2.setHpr(-90, 0, 0)
		#self.node2.setHpr(0, -90, 0)
		#self.node1.setPos(10, 0, -10)

		#self.node1.setHpr((-90,0,0))

		lens1 = PerspectiveLens()
		lens2 = PerspectiveLens()

		lens1.setFov(40)
		lens2.setFov(80)

		lens1.setNearFar(near, far)
		lens2.setNearFar(near, far)

		self.light1 = self.node1.node()
		self.light2 = self.node2.node()

		self.light1.setShadowCaster(True)
		#self.light1.hideFrustrum()
		#self.light1.setShadowCaster(True, 512, 512)
		#self.light1.setLens(PerspectiveLens())
		#self.light1.getLens().setFov(fov)
		#self.light1.getLens().setNearFar(near, far)
		#self.light1.setColor(color)

		self.light1.setExponent(40)
		self.light2.setExponent(60)

		self.light1.setLens(lens1)
		self.light2.setLens(lens2)

		self.light1.setAttenuation((0.5,0.001,0.0001))
		self.light2.setAttenuation((0.5,0.005,0.0010))
		#self.light1.setAttenuation((0, 0.0001, 0.0001))
		#self.light2.setAttenuation((0, 0.0001, 0.0001))

		render.setLight(self.node1)
		#render.setLight(self.node2)

		self.accept('f', self.toggle)

		taskMgr.add(self.updatePower, 'flashlight1/update')

	def toggle(self):
		self.on = not self.on

	def updatePower(self, task):
		elapsed = task.time - self.last
		self.last = task.time

		#self.power = max(POWER_MIN, self.power + elapsed * POWER_RATE * self.on)
		self.light1.setColor(self.color * self.power)
		self.light1.setColor(self.color * self.power)

		#self.light1.getLens().setFov(40 + 20 * sin(2 * pi * task.time / 10))
		#self.light2.getLens().setFov(20 + 10 * sin(2 * pi * task.time / 10))

		#self.node1.setPos((0,0, 25 + 100 * sin(2 * pi * task.time / 23)**2))
		#self.node2.setPos((0,0, 25 + 20 * sin(2 * pi * task.time / 23)**2))

		#self.light1.setExponent(70 + 55 * sin(2 * pi * task.time / 10))
		#self.light2.setExponent(70 + 55 * sin(2 * pi * task.time / 10))

		self.node1.setHpr((-90 + 90 * sin(2 * pi * task.time / 15),0,0))
		self.node2.setHpr((-90 + 90 * sin(2 * pi * task.time / 15),0,0))
		#self.node2.setHpr((0, -90 + 45 * sin(2 * pi * task.time / 10),0))

		return task.cont
