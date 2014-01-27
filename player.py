from collections import defaultdict
from direct.filter.CommonFilters import CommonFilters
from direct.interval.IntervalGlobal import Sequence
from direct.interval.LerpInterval import LerpHprInterval, LerpPosInterval
from random import random
import time

from collision import CollisionMask as Mask
from hud import HUD
from lighting import Flashlight
from panda3d.core import BitMask32, CollisionHandlerEvent, \
	CollisionHandlerGravity, CollisionHandlerPhysical, CollisionHandlerPusher, \
	CollisionNode, CollisionSegment, CollisionSphere, CollisionRay, Vec3, Vec4
from scene_obj import SceneObject


FLASH_FEAR_TIME = 0.03
FLASH_FEAR_AMP  = 1.2

#TODO: Restrict Player's movements after death
#TODO: Create one animation for each type of death
#TODO: The class is somewhat long coded. Consider refactoring things as health management, inventory and action management, collisions and movement to separate classes and make Player, mostly, a container for these classes
class Player(SceneObject):
	
	RESTFUL=0
	TIRED=1
	EXHAUSTED=2
	
	STOPPED=0.0
	WALKING=0.07
	RUNNING=0.14
	
	NORMAL   = 1.0
	CRAWLING = 0.5
	
	HEIGHT = 1.8
	CROUCHED_HEIGHT = 0.5
	ARM_LENGTH = HEIGHT = 1.0
	
	FEAR_RATE       = -1.0 / 2.40
	FEAR_INC        = 0.1
	FEAR_SCREAM_MIN = 0.0
	FEAR_FOV_AMP    = 75.0
	
	JUMP_POWER = 3.0
	
	SIGHT_NEAR = HEIGHT/18
	SIGHT_FAR  = 500
	
	#TODO: Refactor constants
	#TODO: Improve collision solids (specially, the feet) and switch between light and dark auras when appropriate
	BODY_SOLID = CollisionSphere (0, 0,  HEIGHT / 2, HEIGHT / 9)
# 	CROUCHED_BODY_SOLID
	DARK_AURA  = CollisionSphere (0, 0,  HEIGHT, HEIGHT * 4)
	LIGHT_AURA = CollisionSphere (0, 0,  HEIGHT, HEIGHT * 4)
	FEET_SOLID = CollisionRay    (0, 0,  HEIGHT / 2, 0, 0, -1)
	JUMP_SOLID = CollisionSegment(0, 0, -HEIGHT / 2, 0, 0, HEIGHT / 2)
	HAND_SOLID = CollisionSegment(0, 0, 0, 0, ARM_LENGTH, 0)
	
	AURA_NODE = 'AuraNode'
	BODY_NODE = 'BodyNode'
	FEET_NODE = 'FeetNode'
	JUMP_NODE = 'JumpNode'
	HAND_NODE = 'HandNode'
	
	DEATH_JUMP_HEIGHT = 3.0
	
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

	def __init__(self, base, scene, name, model='', pos=Vec3(0,0,0), scale=1.0):
		SceneObject.__init__(self, base, scene, name, pos, scale)
		
		#TODO: load the model

		self.startPos = pos
		self.previousHeight = pos.z
		self.breath  = 1.0
		self.fear    = 0.0
		self.speed   = 0.0
		self.stopped = 1.0
		self.life = 10.0
		self.pace = Player.NORMAL

		self.initTimer = True
		self.attacked = False

		self.paused = False
		
		#TODO: Refactor to another class?
		self.inventory = []
		
		#TODO: Should be moved to SceneObj
		self.scene = scene
		
		self.setupCamera(base)
		self.setupCollision()
		self.setupFlashlight()
		self.toggleFlashlight()
		self.setupKeys()
		self.setupSound()
		self.updateState(Player.RESTFUL)
		
		self.filters = CommonFilters(base.win, base.cam)

		self.last = 0
		
		self.dying = 0
		self.dyingInterval1 = LerpHprInterval(self.flashlight.nodepath, 0.2, (5, 5, 0), bakeInStart=False)
		self.dyingInterval2 = LerpHprInterval(self.flashlight.nodepath, 0.2, (5, 5, 0), bakeInStart=False)
			
	def __del__(self):
		self.scene = None
		self.flashlight = None
		
	#TODO: Move this to flashlight class?
	#TODO: Refactor constant values
	def setupFlashlight(self):
		self.flashlight = Flashlight('spot', self, self.scene, (Player.HEIGHT / 7, -Player.HEIGHT / 17.5, -Player.HEIGHT / 7), near=Player.SIGHT_NEAR, far=Player.SIGHT_FAR)
		
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

	def setupCamera(self, base):
		self.cam = base.cam
		self.cam.reparentTo(self.getNodePath())
		self.cam.setPos(Vec3(0,0,Player.HEIGHT + Player.HEIGHT / 2))
		self.cam.node().getLens().setNearFar(Player.SIGHT_NEAR, Player.SIGHT_FAR)
		
	def setupCollision(self):
		self.addCollisionGroup(Player.AURA_NODE, [Player.DARK_AURA ], CollisionHandlerEvent  (), (Mask.NONE , Mask.PLAYER))
		self.addCollisionGroup(Player.BODY_NODE, [Player.BODY_SOLID], CollisionHandlerPusher (), (Mask.SCENE, Mask.PLAYER))
		self.addCollisionGroup(Player.FEET_NODE, [Player.FEET_SOLID], CollisionHandlerGravity(), (Mask.SCENE, Mask.NONE  ))
		self.addCollisionGroup(Player.JUMP_NODE, [Player.JUMP_SOLID], CollisionHandlerEvent  (), (Mask.SCENE, Mask.NONE  ))
		self.addCollisionGroup(Player.HAND_NODE, [Player.HAND_SOLID], CollisionHandlerEvent  (), (Mask.HAND , Mask.NONE  ))
		
		self.feetHandler = self.getCollisionHandler(Player.FEET_NODE)
		self.feetHandler.setGravity(self.base.GRAVITY)
		
		#TODO: Refactor names
		playerhandson  = 'Player-HandsOn'
		playerhandsoff = 'Player-HandsOff'
		
		playerfall = 'Player-Fall'
		playerjump = 'Player-Jump'
		
		handCollider = self.getCollisionNode   (Player.HAND_NODE )
		handHandler  = self.getCollisionHandler(Player.HAND_NODE)
		
		handCollider.reparentTo(self.cam)
		handHandler.addInPattern (playerhandson )
		handHandler.addOutPattern(playerhandsoff)
		
		jumpHandler = self.getCollisionHandler(Player.JUMP_NODE)
		jumpHandler.addInPattern (playerfall)
		jumpHandler.addOutPattern(playerjump)
		
		self.accept(playerfall, self.recordFall)
		self.accept(playerjump, self.recordJump)
	
	def recordJump(self, entry):
		self.previousHeight = entry.getSurfacePoint(self.scene).z
		
	def recordFall(self, entry):
		newHeight = entry.getSurfacePoint(self.scene).z
		if self.previousHeight - newHeight > Player.DEATH_JUMP_HEIGHT:
			self.die()
		self.previousHeight = newHeight
		
	def setupSound(self):
		#sounds of the player
		#TODO: Refactor whole sound system?
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
		
		self.dyingSound = loader.loadSfx("assets/sounds/player/dying.mp3")
		
		self.breathing.setVolume(self.breath_vol - self.breath)
		self.breathing.setPlayRate(0.6)
		self.breathing.setLoop(True)
		self.breathing.play()

	def isTired(self):
		return self.state == Player.TIRED

	def isExhausted(self):
		return self.state == Player.EXHAUSTED

	def isAlive(self):
		#return self.breath > -1
		return self.life > 0.0
	
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
			self.flashfearbang = LerpHprInterval(self.flashlight.nodepath, FLASH_FEAR_TIME, hpr, bakeInStart=False)
			self.flashfearbang.start()
			
	def updateSound(self):
		#Step sound
		if (any(self.keys)):
			self.stopped = 0
			if (self.feetHandler.isOnGround() and \
				self.footsteps[self.actualstep%4].status() != self.footsteps[self.actualstep%4].PLAYING):
				
				self.actualstep += 1
				self.footsteps[self.actualstep%4].setPlayRate(self.speed * 15)
				self.footsteps[self.actualstep%4].play()
		else:
			self.stopped = 1
		
		#Breathing sound
		self.breathing.setVolume(max(self.breath_vol-1,self.breath_vol - self.breath))
		if (self.breath == 0):
			self.breath = 0.01
		self.breathing.setPlayRate(min(1.0, 0.6 * (1/(0.1 + self.breath))))
		
	def updateBreath(self, elapsed):
		oldbreath   = self.breath
		
		deltabreath = self.breathrate * elapsed
		deltafear   = Player.FEAR_RATE       * elapsed

		self.breath = min(1.0, max(-self.fear, self.breath + deltabreath))
		self.fear   = min(1.0, max(       0.0, self.fear   + deltafear  ))
		
		#self.filters.setBlurSharpen( 1.0 - self.fear)
				
	def updateAll(self, task):
		elapsed = task.time - self.last
		self.last = task.time
		
		if (self.dying):
			self.life -= 0.005
			self.filters.setBlurSharpen(self.life-0.2)
			
			if (not self.dyingInterval1.isPlaying() and not self.dyingInterval2.isPlaying()):
				self.dyingInterval1.finish()
				self.dyingInterval2.finish()
				xrot = 10*random() - 5
				yrot = 10*random() - 5
				hpr1 = (self.getNodePath().getHpr().getX()+xrot, 0, 0)
				hpr2 = (0, base.cam.getHpr().getY()+yrot, 0)
			
				self.dyingInterval1 = self.getNodePath().hprInterval(0.01/self.life,hpr1)
				self.dyingInterval2 = base.cam.hprInterval(0.01/self.life,hpr2)
				self.dyingInterval1.start()
				self.dyingInterval2.start()
				
			if (self.isAlive()):
				return task.cont
			else:
				self.filters.delBlurSharpen()
				fadeIn = render.colorScaleInterval(0.1, Vec4(1,1,1,1))
				fadeIn.start()
				return task.done
		
		#TODO: Refactor
		self.cam.node().getLens().setFov(75 + self.fear * Player.FEAR_FOV_AMP)
		
		self.updateBreath(elapsed)
		self.updatePosition(elapsed)
		self.updateFlashBang()
		self.updateSound()

		if (self.attacked):
			timeFinished = self.timer()
			if (timeFinished):
				self.life += 1.0
				self.attacked = False
		#print "life: ", self.life

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
		if self.feetHandler.isOnGround(): 
			self.feetHandler.addVelocity(Player.JUMP_POWER)

	def crouch(self, pace):
		if self.feetHandler.isOnGround():
			self.pace = pace
			if pace == Player.NORMAL:
				LerpPosInterval(self.cam, 0.2, (0, 0, Player.HEIGHT)).start()
			else:
				LerpPosInterval(self.cam, 0.2, (0, 0, Player.CROUCHED_HEIGHT)).start()
	
	def boo(self):
		self.fear = min(1.0, self.fear + Player.FEAR_INC)
		if self.fear > Player.FEAR_SCREAM_MIN:
			self.scream()
	
	def scream(self):
		self.screams.play()

	#TODO: Review damage / life system
	def hurt(self):
		self.attacked = True
		self.life -= 1.0
		self.startTimer(5)
		
	def die(self):
		self.breathing.stop()
		self.dyingSound.play()

#TODO: Refactor effects
		fadeOut = render.colorScaleInterval(3, Vec4(1,0,0,1))
		fadeOut.start()
		self.life  = 1
		self.dying = 1

	def timer(self):
		currentTime = time.time()
		diff = currentTime - self.time
# 		print diff
		if (diff > self.interval):
			self.resetTimer()
			return True
		else:
			return False

	def resetTimer(self):
		self.initTimer = True

	def startTimer(self, interval):
		if (self.initTimer == True):
			self.interval = interval
			self.initTimer = False
			self.time = time.time()

	def clean(self):
		for step in self.footsteps:
			loader.unloadSfx(step)      
	
		loader.unloadSfx(self.screams)
		loader.unloadSfx(self.breathing)

	def toggleFlashlight(self):
		self.flashlight.toggle()
		
		if (self.flashlight.isOn()):
			self.setCollisionSolid(Player.AURA_NODE, Player.LIGHT_AURA)
		else:
			self.setCollisionSolid(Player.AURA_NODE, Player.DARK_AURA )
		
	def resetLast(self):
		self.last = 0
		
	def pause(self):
		if (self.paused == True):
			self.paused = False
		else:
			self.paused = True
			
	def isPaused(self):
		return self.paused
