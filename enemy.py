from hooded import *

class Enemy:

	def __init__(self, pos, patrolPos):
		self.seeker = Actor("assets/chicken/vulto-pedro")
		#self.seeker = Actor("models/ralph",{"run":"models/ralph-run", "walk":"models/ralph-walk"})
		self.seeker.setCollideMask(BitMask32.allOff())
		self.pos = pos
		self.pos.z += 10
		self.seeker.setPos(self.pos)
		self.seeker.reparentTo(render)
		#self.seeker.setScale(6)
		self.startPos = self.pos

		self.hooded = Hooded("seeker", self.seeker, 1200, 800, 800)
		self.hooded.initialize()
		self.hooded.setPatrolPos(patrolPos)

	def getHooded(self):
		return self.hooded

	def update(self):
		return self.hooded.update()

	def defineDynamicObjects(self, model, objectsPath):
		self.model = loader.loadModel(model)
		self.doors  = self.model.findAllMatches(objectsPath)
		for o in self.doors:
			self.hooded.addDynamicObject(o)

	def hear(self, noisePos):
		self.hooded.hear(noisePos)

	def start(self):
		self.seeker.setPos(self.startPos)
		self.hooded.start()

	def stop(self):
		self.hooded.stop()

