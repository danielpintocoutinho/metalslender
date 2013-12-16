class CameraControls:

	#TODO: Insert parameters for initial setup?
	def __init__(self, base, player):
		self.base   = base
		self.player = player

		self.xrot = 180
		self.yrot = 0

		self.last = 0

		self.move = False

	def update(self, task):
		md = self.base.win.getPointer(0)
		x = md.getX()
		y = md.getY()

		if self.base.win.movePointer(0, 100, 100):
			self.xrot -= (x - 100) * 0.2
			self.yrot -= (y - 100) * 0.2
			self.yrot = max(-90, min(90, self.yrot))

		self.player.getNodePath().setHpr(self.xrot, 0, 0)
		self.base.cam.setHpr(0, self.yrot, 0)
		
# 		self.base.skydome.setHpr(-self.player.getNodePath().getHpr())

		return task.cont