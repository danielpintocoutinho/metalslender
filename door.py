from direct.actor.Actor import Actor

from constants import *
from collision import CollisionMask

class Door(Actor):
	
	SOUND_DOOR_OPEN   = 0
	SOUND_DOOR_CLOSE  = 1
	SOUND_DOOR_LOCKED = 2
	SOUND_DOOR_UNLOCK = 3
	
	#TODO: Configure through file?
	SOUND_FILES = {
		SOUND_DOOR_OPEN   : SOUND_DIRECTORY + '/items/door_open.mp3',
		SOUND_DOOR_CLOSE  : SOUND_DIRECTORY + '/items/door_close.mp3',
		SOUND_DOOR_LOCKED : SOUND_DIRECTORY + '/items/door_force.mp3',
		SOUND_DOOR_UNLOCK : SOUND_DIRECTORY + '/items/door_unlock.mp3'
	}
	
	def __init__(self, base, np):
		sgn = 'Neg' if np.hasTag('DoorNeg') else 'Pos'
		amp = np.getTag('DoorAmp') if np.hasTag('DoorAmp') else 90
		key = np.getTag('DoorKey')

		anim = { 
			'Door' : {
				'Open'  : EGG_DOOR + '-Open'  + amp + sgn,
				'Close' : EGG_DOOR + '-Close' + amp + sgn
			},
			'Knob' : {
				'Open'  : EGG_KNOB + '-Open'  + amp + sgn,
				'Close' : EGG_KNOB + '-Close' + amp + sgn
			}, 
		}
		
		models = {
			'Door' : EGG_DOOR,
			'Knob' : EGG_KNOB
		}
		
		Actor.__init__(self, models, anim)
		
		self.setName(np.getName())
		self.setPos(np.getPos())
		self.setHpr(np.getHpr())
		self.setScale(np.getScale())
		self.reparentTo(np.getParent())
		
#TODO: Collision is not working on the door
# 		for np in self.findAllMatches('**/-GeomNode'):
# 			np.node().setIntoCollideMask(Mask.WALL | Mask.HAND)
#   		self.find('**/__Actor_Door/-GeomNode').node().setIntoCollideMask(Mask.WALL | Mask.HAND)
		self.np = np
		self.np.node().setIntoCollideMask(CollisionMask.WALL | CollisionMask.HAND)
		self.np.hide()
		
		#TODO: Different sounds for different amplitudes
		self.sounds = {}
		for sound in Door.SOUND_FILES:
			self.sounds[sound] = base.loader.loadSfx(Door.SOUND_FILES[sound])
		
		self.lock = key
		self.closed = True
		
		#TODO: POG: Applying the scale to the door makes the door too small, but when animated, it is scaled back to the proper size
		self.act(None)
		self.act(None)
		
	def __del__(self):
 		self.removeNode()
		
	def act(self, player):
		#TODO: player == None is POG for scale correction 
		if self.lock and player is not None:
			if self.lock in [key.lock for key in player.inventory]:
				self.sounds[Door.SOUND_DOOR_UNLOCK].play()
				self.lock = ''
			else:
				self.sounds[Door.SOUND_DOOR_LOCKED].play()
		else:
			if self.closed:
				self.sounds[Door.SOUND_DOOR_OPEN].play()
				self.play('Open', 'Door')
				self.play('Open', 'Knob')
				self.np.node().setIntoCollideMask(CollisionMask.HAND)
			else:
				self.sounds[Door.SOUND_DOOR_CLOSE].play()
				self.play('Close', 'Door')
				self.play('Close', 'Knob')
				self.np.node().setIntoCollideMask(CollisionMask.WALL | CollisionMask.HAND)
				
			self.closed = not self.closed