from pandac.PandaModules import Vec3
from panda3d.core import BitMask32

from camera import CameraControls
from scene_obj import SceneObj
from hud import HUD

import collisionSystem

from direct.showbase.DirectObject import DirectObject

RESTFUL=0
TIRED=1
EXHAUSTED=2

STOPPED=0
WALKING=1
RUNNING=2.5

breathrates = {
	(RESTFUL  , STOPPED) :  1.0 /  60,
	(RESTFUL  , WALKING) :  1.0 /  80,
	(RESTFUL  , RUNNING) : -1.0 /  20,
	(TIRED    , STOPPED) :  1.0 /  90,
	(TIRED    , WALKING) :  1.0 / 120,
	(TIRED    , RUNNING) : -1.0 /  10,
	(EXHAUSTED, STOPPED) :  1.0 / 120,
	(EXHAUSTED, WALKING) :  1.0 / 160,
	(EXHAUSTED, RUNNING) : -1.0 /   5,
}

#TODO: Refactor things to improve SceneObj
class Player(SceneObj):
	def __init__(self, name, model_path = '' , pos=Vec3(0,0,0), scale=1.0, source=render,actor=False):
		SceneObj.__init__(self, name, model_path, pos, scale, source, actor)

		self.breath  = 1.0
		self.fear    = 0.0
		self.speed   = 1.0
		self.stopped = 1.0

		self.fearrate   = -1.0 / 360

		self.last = 0
		self.keys = [STOPPED] * 4
		
		#sounds of the player
		self.actualstep = 0;
		self.step_vel = 0.7
		step1 = loader.loadSfx("assets/sounds/player/step1.mp3")
		step2 = loader.loadSfx("assets/sounds/player/step2.mp3")
		step3 = loader.loadSfx("assets/sounds/player/step3.mp3")
		step4 = loader.loadSfx("assets/sounds/player/step4.mp3")        
		self.footsteps = [step1,step2,step3,step4]
		
		self.screams = loader.loadSfx("assets/sounds/player/scream_low1.mp3")
		self.breathing = loader.loadSfx("assets/sounds/player/breathing.mp3")
		self.breath_vol = 1.07
		
		self.updateState(RESTFUL)

		self.setObjCollision()
		self.setFloorCollision(collisionSystem.FLOOR_MASK, BitMask32.allOff())
		self.setWallCollision(collisionSystem.WALL_MASK, BitMask32.allOff())

		base.cam.reparentTo(self.getNodePath())
		#BUG: Shadows are cast with a positive offset on the z-axis
		base.cam.setPos(Vec3(0,0,25))

		self.accept("w-up", self.setKeys, [0, 0])
		self.accept("w-up", self.setKeys, [0, 0])
		self.accept("s-up", self.setKeys, [1, 0])
		self.accept("a-up", self.setKeys, [2, 0])
		self.accept("d-up", self.setKeys, [3, 0])
		self.accept("w", self.setKeys, [0, 1])
		self.accept("W", self.setKeys, [0, 1])
		self.accept("s", self.setKeys, [1, 1])
		self.accept("a", self.setKeys, [2, 1])
		self.accept("d", self.setKeys, [3, 1])
		self.accept("c-up", self.setSpeed, [1.0])
		self.accept("c", self.setSpeed, [2.5])
		#TODO: Must taks your breath, also
		self.accept("space", self.jump)

		taskMgr.add(self.taskUpdate, "player/update")
		
		self.breathing.setVolume(self.breath_vol - self.breath)
		self.breathing.setPlayRate(0.6)
		self.breathing.setLoop(True)
		self.breathing.play()

	def isTired(self):
		return self.state == TIRED

	def isExhausted(self):
		return self.state == EXHAUSTED

	def isAlive(self):
		return self.breath > -1

	#TODO: Other methods like isDead()
	
	#TODO: If movement validation is enabled, the player must stop once it is
	# exhausted, which means it cannot run and die of fear. But if it isn't, the
	# player can continue running after it is tired.
	def validateMovement(self):
		if self.isExhausted():
			self.keys = [min(k, WALKING) for k in self.keys]

	def updateState(self, breath):
		self.state = breath
		self.validateMovement()
		self.breathrate = breathrates[(self.state, max(self.keys))]
				 
	def setKeys(self, btn, value):
		self.keys[btn] = value
		#self.validateMovement()
		
	def setSpeed(self, value):
		self.speed = value
				
	def taskUpdate(self, task):
		player = self.getNodePath()
		self.focus = player.getPos()
		#TODO: Bad code! Make the flashlight a child of the player
		#flashlight = render.find("Spot")

		elapsed = task.time - self.last
		self.last = task.time

		if (self.keys[0]):
				dir = player.getMat().getRow3(1) #0 is x, 1 is y, 2 is z,
				dir.setZ(0)
				self.focus = self.focus + dir * elapsed*40 * self.speed
				player.setFluidPos(self.focus)
		if (self.keys[1]):
				dir = player.getMat().getRow3(1)
				dir.setZ(0)
				self.focus = self.focus - dir * elapsed*40 * self.speed
				player.setFluidPos(self.focus)
		if (self.keys[2]):
				dir = player.getMat().getRow3(0)
				dir.setZ(0)
				self.focus = self.focus - dir * elapsed*20 * self.speed
				player.setFluidPos(self.focus)
		if (self.keys[3]):
				dir = player.getMat().getRow3(0)
				dir.setZ(0)
				self.focus = self.focus + dir * elapsed*20 * self.speed
				player.setFluidPos(self.focus)
		
		#Step sound
		if (self.keys[0] or self.keys[1] or self.keys[2] or self.keys[3]):
			self.stopped = 0
			if (self.getFloorHandler().isOnGround() and \
				self.footsteps[self.actualstep%4].status() != self.footsteps[self.actualstep%4].PLAYING):
				
				self.actualstep += 1
				self.footsteps[self.actualstep%4].setPlayRate(self.step_vel * self.speed)
				self.footsteps[self.actualstep%4].play()
		else:
			self.stopped = 1
				
		# positions the flashlight with the player 
		#flashlight.setFluidPos(player.getPos())
		#flashlight.setZ(flashlight.getZ() + 4)
		#flashlight.setHpr( player.getHpr())

		oldbreath   = self.breath
		deltabreath = self.breathrate * elapsed
		deltafear   = self.fearrate   * elapsed
		self.fear   = min(1.0, max(       0.00001, self.fear   + deltafear  ))
		self.breath = min(1.0, max(-self.fear, self.breath + deltabreath))
		
		#Breathing sound
		self.breathing.setVolume(max(self.breath_vol-1,self.breath_vol - self.breath))
		self.breathing.setPlayRate(min(1.0,0.6 * (1/self.breath)))

		if self.isAlive():

			if self.breath > self.fear:
				self.updateState(RESTFUL)
			elif self.breath > 0:
				self.updateState(TIRED)
			elif self.breath >= -self.fear:
				self.updateState(EXHAUSTED)
			#TODO: Send an event saying that it can't run anymore
			else:
				pass

			return task.cont
		else:
			#TODO: send a 'death' event and, possibly, play back a nice heart stopping animation
			return task.done
	
	def jump(self):
		if self.getFloorHandler().isOnGround(): 
			self.getFloorHandler().addVelocity(25)
	
	def scream(self):
		self.screams.play()
