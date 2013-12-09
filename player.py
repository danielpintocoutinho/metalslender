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

FLASH_FEAR_TIME = 0.03
FLASH_FEAR_AMP  = 0.2

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

FEAR_RATE = -1.0 / 30

#TODO: Names that come from Showbase: taskMgr, loader 

#TODO: Refactor things to improve SceneObj
class Player(SceneObj):

	def __init__(self, name, parent, actMng, model='', pos=Vec3(0,0,0), scale=1.0):
		SceneObj.__init__(self, name, model, parent, pos, scale, False)

		self.actMng = actMng
		self.actMng.setPlayer(self)
		self.breath  = 1.0
		self.fear    = 0.0
		self.speed   = 0.0
		self.height  = 35.0
		self.stopped = 1.0
		self.pace = NORMAL
		
		self.setupCamera()
		self.setupFlashlight()
		self.setupKeys()
		self.setupCollistion()
		self.setupSound()
		self.updateState(RESTFUL)

		self.last = 0
		
	#TODO: Move this to flashlight class?
	def setupFlashlight(self):
		self.flashlight = Flashlight('spot', self)
		
		self.flashfearbang = LerpHprInterval(self.flashlight.node1, 0.2, (5, 5, 0), bakeInStart=False)

		bangUp   = LerpHprInterval(self.flashlight.node1, 0.3, (5, 6.5, 0), bakeInStart=False)
		bangDown = LerpHprInterval(self.flashlight.node1, 0.3, (5, 3.5, 0), bakeInStart=False)
		self.flashwalkbang = Sequence(bangUp, bangDown)
		self.flashwalkbang.loop()
		self.flashwalkbang.pause()
		
		bangUp   = LerpHprInterval(self.flashlight.node1, 0.25, (5, 7.5, 0), bakeInStart=False)
		bangDown = LerpHprInterval(self.flashlight.node1, 0.25, (5, 2.5, 0), bakeInStart=False)
		self.flashrunbang = Sequence(bangUp, bangDown)
		self.flashrunbang.loop()
		self.flashrunbang.pause()
	
	def setupKeys(self):
		self.keys = [STOPPED] * 4

	#TODO: Create my own camera and put it into base.cam
	def setupCamera(self):
		self.cam = base.cam
		self.cam.reparentTo(self.getNodePath())
		self.cam.setPos(Vec3(0,0,25))
		
	def setupCollistion(self):
		self.setObjCollision()
		self.setFloorCollision(collisionSystem.FLOOR_MASK, BitMask32.allOff())
		self.setWallCollision(collisionSystem.WALL_MASK, BitMask32.allOff())
		
	def setupSound(self):
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
	def updateState(self, breath):
		self.state = breath
		if self.isExhausted():
			self.keys = min(self.speed, WALKING)
		self.breathrate = breathrates[(self.state, self.speed)]
		
	#TODO: Complex control logic should be moved to a controller class
	def setSpeed(self, speed, key=None, value=True, preserve=True):
		oldspeed = self.speed
		
		if key is not None:
			self.keys[key] = value
		
		if any(self.keys):
			if not preserve or self.speed == STOPPED:
				self.speed = speed
		else:
			self.speed = STOPPED
			
		if oldspeed != WALKING and self.speed == WALKING:
			self.flashrunbang.pause()
			self.flashwalkbang.resume()
		elif oldspeed != RUNNING and self.speed == RUNNING:
			self.flashwalkbang.pause()
			self.flashrunbang.resume()
		elif oldspeed != STOPPED and self.speed == STOPPED:
			self.flashwalkbang.pause()
			self.flashrunbang.pause()
				
	def updatePosition(self, elapsed):
		focus = self.getNodePath().getPos()
		
		np = self.getNodePath()
		
		if (self.keys[0]):
			dir = np.getMat().getRow3(1) #0 is x, 1 is y, 2 is z,
			dir.setZ(0)
			focus += dir * elapsed*40 * self.speed * self.pace
			np.setFluidPos(focus)
		if (self.keys[1]):
			dir = np.getMat().getRow3(1)
			dir.setZ(0)
			focus -= dir * elapsed*40 * self.speed * self.pace
			np.setFluidPos(focus)
		if (self.keys[2]):
			dir = np.getMat().getRow3(0)
			dir.setZ(0)
			focus -= dir * elapsed*20 * self.speed * self.pace
			np.setFluidPos(focus)
		if (self.keys[3]):
			dir = np.getMat().getRow3(0)
			dir.setZ(0)
			focus += dir * elapsed*20 * self.speed * self.pace
			np.setFluidPos(focus)
			
	def updateFlashBang(self):
		if self.fear > 0 and self.flashfearbang.isStopped():
			self.flashfearbang.finish()
			hprx = 5 * (1 + FLASH_FEAR_AMP * self.fear * random())
			hpry = 5 * (1 + FLASH_FEAR_AMP * self.fear * random())
			hpr = (hprx, hpry, 0)
			self.flashfearbang = LerpHprInterval(self.flashlight.node1, FLASH_FEAR_TIME, hpr, bakeInStart=False)
			self.flashfearbang.start()
			
	def updateSound(self):
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
		
		#Breathing sound
		self.breathing.setVolume(max(self.breath_vol-1,self.breath_vol - self.breath))
		self.breathing.setPlayRate(min(1.0,0.6 * (1/self.breath)))
		
	def updateBreath(self, elapsed):
		oldbreath   = self.breath
		deltabreath = self.breathrate * elapsed
		deltafear   = FEAR_RATE   * elapsed
		self.fear   = min(1.0, max(   0.00001, self.fear   + deltafear  ))
		self.breath = min(1.0, max(-self.fear, self.breath + deltabreath))
				
	def updateAll(self, task):
		elapsed = task.time - self.last
		self.last = task.time
		
		self.updateBreath(elapsed)
		self.updatePosition(elapsed)
		self.updateFlashBang()
		self.updateSound()

		#TODO: Review player logic
		if self.isAlive():
			if self.breath > self.fear:
				self.updateState(RESTFUL)
			elif self.breath > 0:
				self.updateState(TIRED)
			elif self.breath >= -self.fear:
				self.updateState(EXHAUSTED)
			#TODO: Send an event saying that it can't run anymore?
			else:
				pass

			return task.cont
		else:
			#TODO: send a 'death' event and, possibly, play back a nice heart stopping animation
			return task.done
	
	def jump(self):
		if self.getFloorHandler().isOnGround(): 
			self.getFloorHandler().addVelocity(30)

	#BUG: Sometimes, player is floating
	#TODO: Model must also be adjusted to get shorter / taller
	def crouch(self, pace):
		if self.getFloorHandler().isOnGround():
			self.pace = pace
			if pace == NORMAL:
				LerpPosInterval(base.cam, 0.2, (0,0,self.height)).start()
			else:
				LerpPosInterval(base.cam, 0.2, (0,0,10)).start()
	
	def scream(self):
		self.screams.play()
		
	def action(self):
		#base.door1.open()
		self.actMng.act()
