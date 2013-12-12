from collections import defaultdict

from direct.interval.IntervalGlobal import Sequence
from direct.interval.LerpInterval import LerpHprInterval, LerpPosInterval
from panda3d.core import BitMask32, CollisionSphere, Vec3

from random import random
from collision import CollisionMask as Mask
from hud import HUD
from lighting import Flashlight
from scene_obj import SceneObject

FLASH_FEAR_TIME = 0.03
FLASH_FEAR_AMP  = 0.2

class Player(SceneObject):
	
	RESTFUL=0
	TIRED=1
	EXHAUSTED=2
	
	STOPPED=0.0
	WALKING=7.5
	RUNNING=3.5
	
	NORMAL   = 1.0
	CRAWLING = 0.5
	
	HEIGHT = 35.0
	CROUCHED_HEIGHT = 10.0
	FEAR_RATE = -1.0 / 30
	
	JUMP_POWER = 40.0
	
	#TODO: Review this recovery system
	breathrates = defaultdict(float)
	breathrates[(RESTFUL  , STOPPED)] = 1.0 /  60
	breathrates[(RESTFUL  , WALKING)] = 1.0 /  80
	breathrates[(RESTFUL  , RUNNING)] =-1.0 /  20
	breathrates[(TIRED    , STOPPED)] = 1.0 /  90
	breathrates[(TIRED    , WALKING)] = 1.0 / 120
	breathrates[(TIRED    , RUNNING)] =-1.0 /  10
	breathrates[(EXHAUSTED, STOPPED)] = 1.0 / 120
	breathrates[(EXHAUSTED, WALKING)] = 1.0 / 160
	breathrates[(EXHAUSTED, RUNNING)] =-1.0 /   5

	def __init__(self, base, name, scene, model='', pos=Vec3(0,0,0), scale=1.0):
		SceneObject.__init__(self, base, name, model, scene, pos, scale)

		self.breath  = 1.0
		self.fear    = 0.0
		self.speed   = 0.0
		self.stopped = 1.0
		self.pace = Player.NORMAL
		
		#TODO: Should be moved to SceneObj
		self.scene = scene
		
		self.setupCamera(base)
		self.setupFlashlight()
		self.setupKeys()
		self.setupCollistion()
		self.setupSound()
		self.updateState(Player.RESTFUL)

		self.last = 0
		
	#TODO: add method boo!
		
	#TODO: Move this to flashlight class?
	def setupFlashlight(self):
		self.flashlight = Flashlight('spot', self, self.scene)
		
		self.flashfearbang = LerpHprInterval(self.flashlight.nodepath, 0.2, (5, 5, 0), bakeInStart=False)

		bangUp   = LerpHprInterval(self.flashlight.nodepath, 0.3, (5, 6.5, 0), bakeInStart=False)
		bangDown = LerpHprInterval(self.flashlight.nodepath, 0.3, (5, 3.5, 0), bakeInStart=False)
		self.flashwalkbang = Sequence(bangUp, bangDown)
		self.flashwalkbang.loop()
		self.flashwalkbang.pause()
		
		bangUp   = LerpHprInterval(self.flashlight.nodepath, 0.25, (5, 7.5, 0), bakeInStart=False)
		bangDown = LerpHprInterval(self.flashlight.nodepath, 0.25, (5, 2.5, 0), bakeInStart=False)
		self.flashrunbang = Sequence(bangUp, bangDown)
		self.flashrunbang.loop()
		self.flashrunbang.pause()
	
	def setupKeys(self):
		self.keys = [Player.STOPPED] * 4

	#TODO: Create my own camera and put it into base.cam
	def setupCamera(self, base):
		self.cam = base.cam
		self.cam.reparentTo(self.getNodePath())
		self.cam.setPos(Vec3(0,0,Player.HEIGHT))
		
	def setupCollistion(self):
		#TODO: Use a Polygon, instead
# 		self.addCollisionSolid(CollisionSphere(0, 0, 0, Player.HEIGHT / 7))
		self.addCollisionSolid(CollisionSphere(0, 0, 0, 4))
# 		self.addCollisionSolid(CollisionTube(0, 0, 0, 0, 0, Player.HEIGHT, Player.HEIGHT / 7))
# 		self.addCollisionSolid(CollisionTube(0, 0, 0, 0, 0, Player.HEIGHT, Player.HEIGHT / 7))
		self.addCollisionRay()
		self.setFloorCollision(fromMask=Mask.FLOOR)
		self.setWallCollision(fromMask=Mask.WALL, intoMask=Mask.SENTINEL)
		
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
		return self.state == Player.TIRED

	def isExhausted(self):
		return self.state == Player.EXHAUSTED

	def isAlive(self):
		return self.breath > -1

	#TODO: Other methods like isDead()
	
	#TODO: If movement validation is enabled, the player must stop once it is
	# exhausted, which means it cannot run and die of fear. But if it isn't, the
	# player can continue running after it is tired.
	def updateState(self, breath):
		self.state = breath
		if self.isExhausted():
			self.keys = min(self.speed, Player.WALKING)
		self.breathrate = Player.breathrates[(self.state, self.speed)]
		
	#TODO: Complex control logic should be moved to a controller class
	def setSpeed(self, speed, key=None, value=True, preserve=True):
		oldspeed = self.speed
		
		if key is not None:
			self.keys[key] = value
		
		if any(self.keys):
			if not preserve or self.speed == Player.STOPPED:
				self.speed = speed
		else:
			self.speed = Player.STOPPED
			
		if oldspeed != Player.WALKING and self.speed == Player.WALKING:
			self.flashrunbang.pause()
			self.flashwalkbang.resume()
		elif oldspeed != Player.RUNNING and self.speed == Player.RUNNING:
			self.flashwalkbang.pause()
			self.flashrunbang.resume()
		elif oldspeed != Player.STOPPED and self.speed == Player.STOPPED:
			self.flashwalkbang.pause()
			self.flashrunbang.pause()
				
	def updatePosition(self, elapsed):
		focus = self.getNodePath().getPos()
		
		np = self.getNodePath()
		#print np.getPos(render)
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
			if (self.floorHandler.isOnGround() and \
				self.footsteps[self.actualstep%4].status() != self.footsteps[self.actualstep%4].PLAYING):
				
				self.actualstep += 1
				self.footsteps[self.actualstep%4].setPlayRate(self.step_vel * self.speed * self.pace)
				self.footsteps[self.actualstep%4].play()
		else:
			self.stopped = 1
		
		#Breathing sound
		self.breathing.setVolume(max(self.breath_vol-1,self.breath_vol - self.breath))
		self.breathing.setPlayRate(min(1.0, 0.6 * (1/self.breath)))
		
	def updateBreath(self, elapsed):
		oldbreath   = self.breath
		
		deltabreath = self.breathrate * elapsed
		deltafear   = Player.FEAR_RATE       * elapsed

		self.breath = min(1.0, max(-self.fear, self.breath + deltabreath))
		self.fear   = min(1.0, max(       0.0, self.fear   + deltafear  ))
				
	def updateAll(self, task):
		elapsed = task.time - self.last
		self.last = task.time
		
		#TODO: Refactor
		self.cam.node().getLens().setFov(75 + self.fear * 95)
		
		self.updateBreath(elapsed)
		self.updatePosition(elapsed)
		self.updateFlashBang()
		self.updateSound()

		#TODO: Review player logic
		if self.isAlive():
			if self.breath > self.fear:
				self.updateState(Player.RESTFUL)
			elif self.breath > 0:
				self.updateState(Player.TIRED)
			elif self.breath >= -self.fear:
				self.updateState(Player.EXHAUSTED)
			#TODO: Send an event saying that it can't run anymore?
			else:
				pass

			return task.cont
		else:
			#TODO: send a 'death' event and, possibly, play back a nice heart stopping animation
			return task.done
	
	def jump(self):
		if self.floorHandler.isOnGround(): 
			self.floorHandler.addVelocity(Player.JUMP_POWER)

	#BUG: Sometimes, player is floating
	#TODO: Model must also be adjusted to get shorter / taller
	def crouch(self, pace):
		if self.floorHandler.isOnGround():
			self.pace = pace
			if pace == Player.NORMAL:
				LerpPosInterval(self.cam, 0.2, (0,0,Player.HEIGHT)).start()
			else:
				LerpPosInterval(self.cam, 0.2, (0,0,Player.CROUCHED_HEIGHT)).start()
	
	def scream(self):
		self.screams.play()
