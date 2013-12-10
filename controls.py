from direct.showbase.DirectObject import DirectObject
from player import WALKING, STOPPED, RUNNING, CRAWLING, NORMAL

class PlayerControls(DirectObject):
	#TODO: Player controls may be customized via an options screen or startup file
	def __init__(self, player):
		self.player = player
		
		self.accept("w-up", self.player.setSpeed, [STOPPED, 0, False])
		self.accept("s-up", self.player.setSpeed, [STOPPED, 1, False])
		self.accept("a-up", self.player.setSpeed, [STOPPED, 2, False])
		self.accept("d-up", self.player.setSpeed, [STOPPED, 3, False])
		
		self.accept("w", self.player.setSpeed, [WALKING, 0, True])
		self.accept("s", self.player.setSpeed, [WALKING, 1, True])
		self.accept("a", self.player.setSpeed, [WALKING, 2, True])
		self.accept("d", self.player.setSpeed, [WALKING, 3, True])
		
		self.accept("shift-w", self.player.setSpeed, [RUNNING, 0, True, False])
		self.accept("shift-s", self.player.setSpeed, [RUNNING, 1, True, False])
		self.accept("shift-a", self.player.setSpeed, [RUNNING, 2, True, False])
		self.accept("shift-d", self.player.setSpeed, [RUNNING, 3, True, False])
		
		self.accept("shift-up", self.player.setSpeed, [WALKING, None, True, False])
		self.accept("shift"   , self.player.setSpeed, [RUNNING, None, True, False])
		
		#TODO: Must take your breath, also
		self.accept("shift-space"  , self.player.jump)
		self.accept("space"        , self.player.jump)
		
		self.accept("shift-c"    , self.player.crouch, [CRAWLING])
		self.accept("c"          , self.player.crouch, [CRAWLING])
		self.accept("c-up"       , self.player.crouch, [NORMAL  ])
		self.accept("shift-c-up" , self.player.crouch, [NORMAL  ])
		
		self.accept("shift-e" , self.player.action)
		self.accept("e"       , self.player.action)
		
		self.accept('f'      , self.player.flashlight.toggle)
		self.accept('shift-f', self.player.flashlight.toggle)