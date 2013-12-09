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