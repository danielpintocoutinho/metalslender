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
		
		self.accept('f'      , self.player.flashlight.toggle)
		self.accept('shift-f', self.player.flashlight.toggle)

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