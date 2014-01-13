from panda3d.core import CollisionNode, CollisionSphere

from direct.showbase.DirectObject import DirectObject
from direct.showbase import Audio3DManager
from direct.task import Task
from direct.interval.IntervalGlobal import Sequence

from collision import CollisionMask

class Collectible(DirectObject):
	
	def __init__(self,base, np, pickSound):
		#TODO: Bad variable naming
		self.model = np
		
		#TODO: Refactor constants and collision solid
		self.collisionNd = CollisionNode(np.getName() + 'ItemSolid')
		self.collisionNP = self.model.attachNewNode(self.collisionNd)
		self.collisionNd.addSolid(CollisionSphere(0, 0, 0, 0.3))
		self.collisionNd.setIntoCollideMask(CollisionMask.HAND)
		
		self.pickedSound = base.loader.loadSfx(pickSound)
		self.picked = False
		
	def __del__(self):
		self.model.removeNode()
		self.pickedSound = None
		
	#TODO: Make Collectible a subclass of NodePath?
	#TODO: The CollisionSolid might also be named after the nodepath
	def getName(self):
		return self.collisionNP.getName()
		
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