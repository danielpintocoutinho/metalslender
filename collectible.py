from panda3d.core import CollisionNode, CollisionSphere
from direct.showbase.DirectObject import DirectObject

from collision import CollisionMask

class Collectible:
	
	def __init__(self, base, model, pickSound):
		self.model = model
		
		#TODO: Refactor constants and collision solid
		self.collisionNd = CollisionNode(model.getName())
		self.collisionNP = self.model.attachNewNode(self.collisionNd)
		self.collisionNd.addSolid(CollisionSphere(0, 0, 0, 0.3))
		self.collisionNd.setIntoCollideMask(CollisionMask.HAND)
		
		self.pickedSound = base.loader.loadSfx(pickSound)
		self.picked = False
		
	def __del__(self):
		self.model.removeNode()
		self.pickedSound = None
		
	def reset(self):
		self.picked = False
		self.model.show()
		
	#TODO: Make Collectible a subclass of NodePath?
	def getName(self):
		return self.model.getName()
		
	def act(self, player):
		if (not self.picked):
			self.pickedSound.play()
			self.model.hide()
			self.picked = True
			player.inventory.append(self)
		
	def wasPicked(self):
		return self.picked

	def used(self):
		self.picked = False

	def clean(self):
		#self.audio3d.unloadSfx(self.pickedSound)
		#self.audio3d.disable()
		pass