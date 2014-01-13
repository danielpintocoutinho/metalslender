from direct.showbase.DirectObject import DirectObject

class ActionManager(DirectObject):
	
	def __init__(self, base, player, rooms=[]):
		
		self.base   = base
		self.player = player
		
		self.reachableObject = None
		self.accept('Player-HandsOn' , self.handsOn )
		self.accept('Player-HandsOff', self.handsOff)
		
		#TODO: Add gates (just a different type of door) to model
		self.items = {}
		for room in rooms:
			self.items.update({ d.getName() : d for d in room.doors })
			self.items.update({ k.getName() : k for k in room.keys  })

	def handsOn(self, item):
		if self.reachableObject is None:
			print 'Hands on ' + item.getIntoNodePath().getName()  
			self.reachableObject = item.getIntoNodePath()
			
	def handsOff(self, item):
		if self.reachableObject == item.getIntoNodePath():
			print 'Hands off ' + self.reachableObject.getName()
			self.reachableObject = None
		
	def act(self):
		if self.reachableObject is not None:
			np = self.reachableObject
			if np.getName() in self.items:
				self.items[np.getName()].act(self.player)