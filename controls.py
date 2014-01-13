from direct.showbase.DirectObject import DirectObject
from player import Player

collshow=False

class PlayerControls(DirectObject):
	#TODO: Player controls may be customized via an options screen or startup file
	def __init__(self, player, actMng):
		self.player = player
		self.actMng = actMng
		
		self.accept("w-up", self.player.setSpeed, [Player.STOPPED, 0, False])
		self.accept("s-up", self.player.setSpeed, [Player.STOPPED, 1, False])
		self.accept("a-up", self.player.setSpeed, [Player.STOPPED, 2, False])
		self.accept("d-up", self.player.setSpeed, [Player.STOPPED, 3, False])
		
		self.accept("w", self.player.setSpeed, [Player.WALKING, 0, True])
		self.accept("s", self.player.setSpeed, [Player.WALKING, 1, True])
		self.accept("a", self.player.setSpeed, [Player.WALKING, 2, True])
		self.accept("d", self.player.setSpeed, [Player.WALKING, 3, True])
		
		self.accept("shift-w", self.player.setSpeed, [Player.RUNNING, 0, True, False])
		self.accept("shift-s", self.player.setSpeed, [Player.RUNNING, 1, True, False])
		self.accept("shift-a", self.player.setSpeed, [Player.RUNNING, 2, True, False])
		self.accept("shift-d", self.player.setSpeed, [Player.RUNNING, 3, True, False])
		
		self.accept("shift-up", self.player.setSpeed, [Player.WALKING, None, True, False])
		self.accept("shift"   , self.player.setSpeed, [Player.RUNNING, None, True, False])
		
		#TODO: Must take your breath, also
		self.accept("shift-space"  , self.player.jump)
		self.accept("space"        , self.player.jump)
	
		self.accept("shift-c"    , self.player.crouch, [Player.CRAWLING])
		self.accept("c"          , self.player.crouch, [Player.CRAWLING])
		self.accept("c-up"       , self.player.crouch, [Player.NORMAL  ])
		self.accept("shift-c-up" , self.player.crouch, [Player.NORMAL  ])
		
		self.accept("shift-e" , self.actMng.act)
		self.accept("e"       , self.actMng.act)
		
		self.accept('f'      , self.player.toggleFlashlight)
		self.accept('shift-f', self.player.toggleFlashlight)

		self.accept('t', self.toggle_collisions)

	def toggle_collisions(self):
		global collshow
		collshow=not collshow
		if collshow:
			base.cTrav.showCollisions(base.render)
			l=base.render.findAllMatches("**/+CollisionNode")
			for cn in l: cn.show()
		else:
			base.cTrav.hideCollisions()
			l=base.render.findAllMatches("**/+CollisionNode")
			for cn in l: cn.hide()
	
	def __del__(self):
		self.player = None
		self.actMng = None

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
		if (self.player.isPaused() == True):
			self.player.pause()
			self.base.win.movePointer(0, 100, 100)
			return task.cont
		
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
	
	def __del__(self):
		self.base = None
		self.player = None