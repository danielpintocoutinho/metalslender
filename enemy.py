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

		self.hooded = Hooded("seeker", self.seeker, 60, 2, 2)
		self.hooded.setPatrolPos(patrolPos)
		
	def __del__(self):
		self.seeker.removeNode()
		self.hooded = None
		self.model.removeNode()		

	def getHooded(self):
		return self.hooded

	def update(self):
		return self.hooded.update()

	def addDynamicObjects(self, objects):
		for o in objects:
			self.hooded.addDynamicObject(o)

	def hear(self, noisePos):
		self.hooded.hear(noisePos)

	def start(self):
		self.seeker.setPos(self.startPos)
		self.hooded.start()

	def stop(self):
		self.hooded.stop()