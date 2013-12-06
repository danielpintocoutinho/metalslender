from pandac.PandaModules import Vec3
from panda3d.core import BitMask32

from math import sin,pi
from random import random

from lighting import Flashlight
from scene_obj import SceneObj
from hud import HUD

import collisionSystem

from direct.showbase.DirectObject import DirectObject
from direct.interval.LerpInterval import LerpPosInterval
from direct.interval.LerpInterval import LerpHprInterval
from direct.interval.IntervalGlobal import Sequence

FLASH_FEAR_TIME = 0.1
FLASH_FEAR_AMP  = 1.5

RESTFUL=0
TIRED=1
EXHAUSTED=2

STOPPED=0.0
WALKING=1.0
RUNNING=2.0

NORMAL   = 1.0
CRAWLING = 0.5

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
	def __init__(self, name, model, source, pos=Vec3(0,0,0), scale=1.0, actor=False):
		SceneObj.__init__(self, name, model, source, pos, scale, actor)

		self.cam = base.cam
		self.breath  = 1.0
		self.fear    = 1.0
		self.speed   = 1.0
		self.stopped = 1.0
		self.pace = NORMAL
		self.flashlight = Flashlight('spot', self)
		
		self.flashinterval = LerpHprInterval(self.flashlight.node1, 0.2, (5, 5, 0))
		self.flashinterval.start()
# 		bangUp   = LerpHprInterval(self.flashlight.node1, 0.3, (5, 6.5, 0))
# 		bangDown = LerpHprInterval(self.flashlight.node1, 0.3, (5, 3.5, 0))
# 		self.flashwalksequence = Sequence(bangUp, bangDown)
# 		self.flashwalksequence.loop()
# 		self.flashwalksequence.pause()
		
# 		bangUp   = LerpHprInterval(self.flashlight.node1, 0.25, (5, 7.5, 0))
# 		bangDown = LerpHprInterval(self.flashlight.node1, 0.25, (5, 2.5, 0))
# 		self.flashwalksequence = Sequence(bangUp, bangDown)
# 		self.flashwalksequence.loop()
# 		self.flashwalksequence.pause()

		self.fearrate   = -1.0 / 30

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

		self.accept("W-up", self.setKeys, [0, 0, STOPPED])
		self.accept("w-up", self.setKeys, [0, 0, STOPPED])
		self.accept("s-up", self.setKeys, [1, 0, STOPPED])
		self.accept("a-up", self.setKeys, [2, 0, STOPPED])
		self.accept("d-up", self.setKeys, [3, 0, STOPPED])
		self.accept("w", self.setKeys, [0, 1, WALKING])
		self.accept("s", self.setKeys, [1, 1, WALKING])
		self.accept("a", self.setKeys, [2, 1, WALKING])
		self.accept("d", self.setKeys, [3, 1, WALKING])
		self.accept("shift-w", self.setKeys, [0, 1, RUNNING])
		self.accept("shift-s", self.setKeys, [1, 1, RUNNING])
		self.accept("shift-a", self.setKeys, [2, 1, RUNNING])
		self.accept("shift-d", self.setKeys, [3, 1, RUNNING])
		self.accept("shift-up", self.setSpeed, [WALKING])
		self.accept("shift", self.setSpeed, [RUNNING])
		#TODO: Must taks your breath, also
		self.accept("space", self.jump)
		self.accept("c", self.crouch, [CRAWLING])
		self.accept("c-up", self.crouch, [NORMAL])

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
				 
	def setKeys(self, btn, value, speed):
		self.keys[btn] = value
		self.speed = speed
		#self.validateMovement()
		
	def setSpeed(self, value):
		self.speed = value
				
	def taskUpdate(self, task):
		player = self.getNodePath()
		self.focus = player.getPos()

		elapsed = task.time - self.last
		self.last = task.time
		
# 		base.camLens.setFov(90 + 35 * sin(2 * task.time * pi / 10))
		if self.flashinterval.isStopped():
			self.flashinterval.finish()
			hprx = 5 * (1 + FLASH_FEAR_AMP * self.fear * random())
			hpry = 5 * (1 + FLASH_FEAR_AMP * self.fear * random())
			hpr = (hprx, hpry, 0)
			self.flashinterval = LerpHprInterval(self.flashlight.node1, FLASH_FEAR_TIME, hpr)
			self.flashinterval.start()
			
# 		if self.speed == WALKING or self.speed == RUNNING:
# 			if not self.flashwalksequence.isPlaying():
# 				self.flashwalksequence.resume()
# 		elif self.speed == STOPPED:
# 			if self.flashwalksequence.isPlaying():
# 				self.flashwalksequence.pause()
# 		self.flashlight.setHpr((5 * (1 + self.fear * random()), 5 * (1 + self.fear * random()), 0))

		if (self.keys[0]):
				dir = player.getMat().getRow3(1) #0 is x, 1 is y, 2 is z,
				dir.setZ(0)
				self.focus = self.focus + dir * elapsed*40 * self.speed * self.pace
				player.setFluidPos(self.focus)
		if (self.keys[1]):
				dir = player.getMat().getRow3(1)
				dir.setZ(0)
				self.focus = self.focus - dir * elapsed*40 * self.speed * self.pace
				player.setFluidPos(self.focus)
		if (self.keys[2]):
				dir = player.getMat().getRow3(0)
				dir.setZ(0)
				self.focus = self.focus - dir * elapsed*20 * self.speed * self.pace
				player.setFluidPos(self.focus)
		if (self.keys[3]):
				dir = player.getMat().getRow3(0)
				dir.setZ(0)
				self.focus = self.focus + dir * elapsed*20 * self.speed * self.pace
				player.setFluidPos(self.focus)
		
		#Step sound
		if (any(self.keys)):
			self.stopped = 0
			if (self.getFloorHandler().isOnGround() and \
				self.footsteps[self.actualstep%4].status() != self.footsteps[self.actualstep%4].PLAYING):
				
				self.actualstep += 1
				self.footsteps[self.actualstep%4].setPlayRate(self.step_vel * self.speed * self.pace)
				self.footsteps[self.actualstep%4].play()
		else:
			self.stopped = 1

		oldbreath   = self.breath
		deltabreath = self.breathrate * elapsed
		deltafear   = self.fearrate   * elapsed
		self.fear   = min(1.0, max(   0.00001, self.fear   + deltafear  ))
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
	
	#TODO: The Jump effect is very lousy
	def jump(self):
		if self.getFloorHandler().isOnGround(): 
			self.getFloorHandler().addVelocity(25)

	#TODO: Model must also be adjusted to get shorter / taller
	def crouch(self, pace):
		if self.getFloorHandler().isOnGround():
			self.pace = pace
			if pace == NORMAL:
				LerpPosInterval(base.cam, 0.2, (0,0,25)).start()
			else:
				LerpPosInterval(base.cam, 0.2, (0,0,10)).start()
	
	def scream(self):
		self.screams.play()
