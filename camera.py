from direct.showbase.DirectObject import DirectObject

class CameraControls(DirectObject):

	#TODO: Insert parameters for initial setup?
	def __init__(self, player):
		self.player = player

		self.xrot = 180
		self.yrot = 0

		self.last = 0

		self.move = False

		taskMgr.add(self.control, "camera/control")

	def control(self, task):
		md = base.win.getPointer(0)
		x = md.getX()
		y = md.getY()

		if (self.move):
			if base.win.movePointer(0, 100, 100):
				self.xrot -= (x - 100) * 0.2
				self.yrot -= (y - 100) * 0.2
				self.yrot = max(-90, min(90, self.yrot))

			self.player.getNodePath().setHpr(self.xrot, 0, 0)
			base.cam.setHpr(0, self.yrot, 0)


		return task.cont

	def setMouseMovement(self, movement):
		self.move = movement
