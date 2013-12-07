from panda3d.core import *
from direct.showbase.DirectObject import DirectObject

spotlights = {}
alight = None

class Lighting(DirectObject):
	
	def addSpotlight(self, name, source, color = Vec4(0.2, 0.2, 0.15, 1), fov =	70, near = 0.01, far = 10):
		spotlight = source.attachNewNode(Spotlight(name))
		spotlight.node().setScene(source)
		#spotlight.node().setShadowCaster(True)
		spotlight.node().hideFrustum()
		spotlight.node().setColor(color)
		spotlight.node().getLens().setFov(fov)
		spotlight.node().getLens().setNearFar(near, far)
		render.setLight(spotlight)
		spotlights[name] = spotlight
	
	def getSpotlight(self, name):
		return spotlights[name]
	
	def setAmbientlight(self, color = Vec4(0.5, 0.5, 0.5, 1)):
		alight = render.attachNewNode(AmbientLight("Ambient"))
		alight.node().setColor(Vec4(0.1, 0.1, 0.1, 1))
		render.setLight(alight)
