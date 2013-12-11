from direct.actor import Actor
from pandac.PandaModules import Vec3
from pandac.PandaModules import ActorNode, CollisionHandlerQueue, CollisionHandlerGravity, CollisionHandlerPusher, CollisionNode, CollisionSphere, CollisionTraverser, BitMask32, CollisionRay
import scene_obj

class SceneActor(scene_obj.SceneObj):

	def __init__(self, name, model, source, pos, scale, animations):
		'''
		Constructor
		'''
		scene_obj.SceneObj.__init__(self, name, "", source, None, None, True)
		
		self.model=Actor.Actor(model, animations)
		self.model.setCollideMask(BitMask32.allOff())
		self.setNodePathPos(pos)
		self.setModelPos(Vec3(0,0,0))
		self.model.reparentTo(self.modelNP)
		self.setScale(scale)
		self.intervals = {}
		self.hasModel = True

	def play(self, name):
		return self.model.play(name)
	
	def loop(self, name, begin = None, end = None, redo = 1):
		return self.model.loop(name, restart = redo, fromFrame = begin, toFrame = last)
	
	def stop (self):
		self.model.stop()
	
	def setAnimInterval(self, name, rate = 1.0):
		return self.model.actorInterval(name,playRate=rate)
	
	def toggleInterval(self, ival):
		if (ival.isPlaying()):
			ival.pause()
		else:
			ival.resume()
	
	def getActor(self):
		return self.model
