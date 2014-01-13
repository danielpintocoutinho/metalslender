from panda3d.core import *
from math import *
import sys,os

from direct.actor.Actor import Actor

from direct.showbase.DirectObject import DirectObject
from direct.showbase import Audio3DManager
from direct.task import Task
from direct.interval.IntervalGlobal import Sequence

from constants import *
from scene_obj import *
from collision import CollisionMask

class Door(Actor):
	
	def __init__(self, base, np):
			#TODO: Use the Door tag to specify the Door model (currently there is only one)
			#TODO: Include sign tag
# 			doortag = np.getTag('Door')
		sgn = 'Neg' if np.hasTag('DoorNeg') else 'Pos'
		amp = np.getTag('DoorAmp')# if np.hasTag('DoorAmp') else 90
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
		
		#TODO: If we can set up the collision using the loaded geometry, this node path can be removed
# 		self.np = np
# 		self.np.hide()
#TODO: Collision is not working on the door
# 		for np in self.findAllMatches('**/-GeomNode'):
# 			np.node().setIntoCollideMask(Mask.WALL | Mask.HAND)
#   		self.find('**/__Actor_Door/-GeomNode').node().setIntoCollideMask(Mask.WALL | Mask.HAND)
		self.np = np
		self.np.node().setIntoCollideMask(Mask.WALL | Mask.HAND)
		self.np.hide()
		
		#TODO: Different sounds for different amplitudes
		#TODO: Refactor sound names to constants and dictionary of sounds
		self.openSound   = base.loader.loadSfx('assets/sounds/items/door_open.mp3')
		self.closeSound  = base.loader.loadSfx('assets/sounds/items/door_close.mp3')
		self.forcesound  = base.loader.loadSfx('assets/sounds/items/door_force.mp3')
		self.unlockSound = base.loader.loadSfx('assets/sounds/items/door_unlock.mp3')
		
		self.lock = key
		self.closed = True
		
		#TODO: POG: Applying the scale to the door makes the door too small, but when animated, it is scaled back to the proper size
		self.act(None)
		self.act(None)
		
	#TODO: Doors must be reset, not removed
	def __del__(self):
 		self.removeNode()
		self.openSound = None
		self.closeSound = None
# 		self.knobSequence = None
		
	#TODO: include keys usage
	def act(self, player):
		
		#TODO: player == None is POG for scale correction 
		if self.lock and player is not None:
			if self.lock in [key.lock for key in player.inventory]:
				self.unlockSound.play()
				self.lock = ''
			else:
				self.forcesound.play()
		else:
			if self.closed:
				self.openSound.play()
				self.play('Open', 'Door')
				self.play('Open', 'Knob')
				self.np.node().setIntoCollideMask(Mask.HAND)
			else:
				self.closeSound.play()
				self.play('Close', 'Door')
				self.play('Close', 'Knob')
				self.np.node().setIntoCollideMask(Mask.WALL | Mask.HAND)
				
			self.closed = not self.closed

	def clean(self):
		#self.audio3d.unloadSfx(self.openSound)
		#self.audio3d.unloadSfx(self.closeSound)
		#self.audio3d.disable()
		pass