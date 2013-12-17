from hooded import *

class Enemy:

	def __init__(self, pos, patrolPos):
		self.seeker = Actor("assets/chicken/hooded")
		#self.seeker = Actor("models/ralph",{"run":"models/ralph-run", "walk":"models/ralph-walk"})
		self.seeker.setCollideMask(BitMask32.allOff())
		self.seeker.setPos(pos)
		self.seeker.reparentTo(render)
		self.seeker.setScale(6)

		self.hooded = Hooded("seeker",self.seeker, 20, 5, 5)
		self.hooded.initialize()
		self.hooded.setPatrolPos(patrolPos)

	def getHooded(self):
		return self.hooded

	def update(self):
		self.hooded.update()

	def defineDynamicObjects(self, model, objectsPath):
		self.model = loader.loadModel(model)
		self.doors  = self.model.findAllMatches(objectsPath)
		for o in self.doors:
			self.hooded.addDynamicObject(o)

	def hear(self, noisePos):
		self.hooded.hear(noisePos)
		
	def __del__(self):
		self.seeker.removeNode()
		self.hooded = None
		self.model.removeNode()
		self.doors = None