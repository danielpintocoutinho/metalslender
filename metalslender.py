#!/usr/bin/ppython
import gc
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import *
from panda3d.ai import *
from panda3d.core import AmbientLight, Vec3, Vec4, Mat4, CollisionTraverser, \
	WindowProperties, AntialiasAttrib, Fog, Texture, TextureStage

from MainMenu import MainMenu
from actionsManager import ActionManager
from camera import CameraControls
from controls import PlayerControls
from door import Door
from enemy import Enemy
from eventsManager import EventManager
from hud import HUD
import interface
from player import Player
from room import Room
import time
import math

# loadPrcFileData("", "prefer-parasite-buffer #f")
#TODO: Review these files
CAM_NEAR=0.1
CAM_FAR =1000

CAM_NEAR = 0.1
CAM_FAR  = 1000

class MetalSlender(ShowBase):
	
	VERSION=0.1
	
	def __init__(self):
		ShowBase.__init__(self)
		self.cTrav = CollisionTraverser()
		self.initConfig()
		self.initGame()

	def initGame(self):
		# Preliminary capabilities check.
		#if not self.initMessages(): 
		#	return
		self.initConfig()

		self.setupEnvironment()
		
		self.AIworld = AIWorld(self.render)

# <<<<<<< HEAD
		self.initTimer = True
		self.time = 0
		self.gameOver = True
# =======
		#TODO: Many things are only done once the game is started
		# Load the scene.
		self.rooms = []
		self.rooms.append(Room(self, "LCG"    , "assets/chicken/lcg" , self.render))
		self.rooms.append(Room(self, "Bloco H", "assets/chicken/blocoh", self.render))
		
		for enemy in self.enemies:
			enemy.defineDynamicObjects("assets/chicken/lcg", "**/LCG_porta*")
		
		#TODO: Support multiple rooms
		self.player  = Player(self, name = "player", pos = Vec3(90,90,12), model='assets/chicken/coelho', scene=self.render)
		self.actions = ActionManager(self, self.rooms[0].model, self.player)
		self.events = EventManager(self, self.player, self.actions)
		self.events.start()
# >>>>>>> refs/remotes/origin/master

		self.setFrameRateMeter(True)
		self.taskMgr.add(self.menuDisplay, "menuDisplay")

# 		self.AIworld.addAiChar(self.enemy.getHooded())

		self.mainMenu = MainMenu(self)
		self.introSound = loader.loadSfx('assets/sounds/intro.mp3')
		self.introSound.setLoop(True)
		self.introSound.play()
		#self.mainMenu.hide()

		# User controls
		self.addCommands()
		
	def setupEnvironment(self):
		#TODO: Not working
# 		self.render.setAntialias(AntialiasAttrib.MMultisample)
		self.setBackgroundColor(0,0,0)
		self.setupLighting()
		self.setupFog()
		self.setupSkydome('assets/chicken/skydome')
		
	def setupFog(self):
		self.fog = Fog("fog")

# 		self.fog.setColor(0.5, 0.1, 0.1)
		self.fog.setColor(0, 0, 0)
		self.fog.setExpDensity(0.004)

# 		self.fog.setLinearRange(0,320)
# 		self.fog.setLinearFallback(45,160,320)
# 		self.cam.attachNewNode(self.fog)

		self.render.setFog(self.fog)
		
	def setupSkydome(self, model):
		self.skydome = self.loader.loadModel(model)
		self.skydome.setBin('background', 0)
		self.skydome.setDepthWrite(False)
		self.skydome.reparentTo(self.cam)
		self.skydome.setCompass()
		self.skydome.setLight(self.shadeless)
		
# 	def setupLighting(self, color = Vec4(0.31, 0.31, 0.31, 1)):
	def setupLighting(self, color = Vec4(0.8, 0.8, 0.8, 1)):
		alight = AmbientLight("AmbientLight")
		alight.setColor(color)
		self.amblight = self.render.attachNewNode(alight)
		self.render.setLight(self.amblight)
		
		#This light may be used by shadeless materials
		alight = AmbientLight("ShadelessLight")
		alight.setColor((1.0,1.0,1.0,1.0))
		self.shadeless = self.render.attachNewNode(alight)
		
	def placeTargets(self):
		self.target1 = self.loader.loadModel("assets/chicken/arrow")
		self.target1.setColor(1,0,0)
		self.target1.setPos(-76.1808, -52.1483, -14.0991)
		self.target1.setScale(5)
		self.target1.reparentTo(self.render)

		# Target2
		self.target2 = self.loader.loadModel("assets/chicken/arrow")
		self.target2.setColor(0,1,0)
		self.target2.setPos(23.3466, -85.0269, -14.0991)
		self.target2.setScale(5)
		self.target2.reparentTo(self.render)

		self.banana = self.loader.loadModel("assets/chicken/banana")
		self.banana.setScale(20)

		self.banana.setPos(23.3466, -85.0269, -14.4758)
		self.banana.reparentTo(self.render)
# >>>>>>> refs/remotes/origin/master

	def initConfig(self):
		self.render.setShaderAuto()
	
		#TODO: Must be moved to player's camera
		#self.camLens.setNearFar(CAM_NEAR,CAM_FAR)
		self.camLens.setFov(75)

		#self.disableMouse()
		self.win.movePointer(0, 100, 100)

		self.props = WindowProperties()

		self.props.setFullscreen(True)
		self.props.setSize(1920, 1080)

		self.props.setCursorHidden(False)
		self.props.setMouseMode(self.props.M_absolute)
		self.paused = False
		
		self.openMainWindow()
		self.graphicsEngine.openWindows()
		self.win.requestProperties(self.props)
		
	def addCommands(self):
		self.accept('escape', self.userExit)
		self.accept('g', self.endGame)
		self.accept('i', self.actionKeys, ['i'])
		self.accept('p', self.pauseGame)
		self.accept('z', self.restartGame)

	def actionKeys(self, key):
		if key == 'i':
			self.player.fear = min(self.player.fear + 0.1, 1.0)
		
	#TODO: Verify if video features are supported
	def initMessages(self):
# 		self.inst_m = menu.addInstructions(0.95 , '[WASD]: walk')
# 		self.inst_h = menu.addInstructions(0.90 , 'SPACE: jump')
# 		self.inst_h = menu.addInstructions(0.85 , 'SHIFT+[WASD]: run' )
# 		self.inst_h = menu.addInstructions(0.80 , 'F: Flashlight On/Off')
# 		self.inst_h = menu.addInstructions(0.75 , 'I: increase fear' )
		return True

	def AIUpdate(self,task):
		hasAttacked = []
		for enemy in self.enemies:
			attack = enemy.update()
			hasAttacked.append(attack)
		#print "novo ciclo"
		for i in hasAttacked:
			if (i == True):
				#print "vai chamar o hurt"
				self.player.hurt()
				#attack
		self.AIworld.update()
		if (not self.taskMgr.hasTaskNamed("player/update")):
			for enemy in self.enemies:
				enemy.stop()
			self.endGame()
			return task.done
		return task.cont

	def newGame(self):
		
		self.introSound.stop()
		initialSound = loader.loadSfx('assets/sounds/enemies/nazgul_scream.mp3')
		initialSound.play()

		self.enemies = []
		self.doors = []
		self.keys = []

		#TODO: Many things are only done once the game is started
		# Load the scene.
		self.rooms = []

		self.rooms.append(Room(self, "LCG"    , "assets/chicken/lcg" , self.render))
		self.rooms.append(Room(self, "Bloco H", "assets/chicken/blocoh", self.render))
		self.rooms.append(Room(self, "Bloco H2", "assets/chicken/blocoh_2andar", self.render))
		
		#self.rooms[1].root.detachNode();
		
		#TODO: adjust code
		for enemy in self.enemies:
			enemy.defineDynamicObjects("assets/chicken/lcg-pedro", "**/LCG_porta*")
		
		#TODO: Support multiple rooms

		self.player  = Player(self, name = "player", model='assets/chicken/coelho', scene=self.render)
		self.actions = ActionManager(self, self.rooms[0].model, self.player,self.rooms)
		self.actions.addDoors(self, self.rooms[1].model, self.doors)
		self.actions.addKeys(self, self.rooms[1].model, self.keys)
		
		self.em = EventManager(self, self.player, self.actions)
		self.em.start()

		self.player.start()
		for enemy in self.enemies:
			enemy.start()

		self.hud      = HUD(self, self.player)
		self.controls = PlayerControls(self.player, self.actions)
		self.camctrl  = CameraControls(self, self.player)

		self.props.setCursorHidden(True)
		self.win.requestProperties(self.props)
# <<<<<<< HEAD
# 		self.mainMenu.hide()
# =======
		self.mainMenu.hideNewGame()
		
		self.taskMgr.add(self.camctrl.update, "camera/control")
	
	def pauseGame(self):
		if (self.paused == True):
			self.props.setCursorHidden(True)
			self.win.requestProperties(self.props)
			self.mainMenu.hidePauseGame()
			self.paused = False
			self.events.start()
			self.taskMgr.add(self.player.updateAll, "player/update")
			self.taskMgr.add(self.hud.update, 'hud')
			self.taskMgr.add(self.player.flashlight.updatePower, 'player/flashlight/update')
			self.taskMgr.add(self.AIUpdate,"AIUpdate")
			self.taskMgr.add(self.camctrl.update, "camera/control")
			self.accept('p', self.pauseGame)
		else:
			self.events.stop()
			self.ignore('p')
			self.player.pause()
			self.taskMgr.remove("camera/control")
			self.taskMgr.remove("player/update")
			self.taskMgr.remove('hud')
			self.player.resetLast()
			self.taskMgr.remove('player/flashlight/update')
			self.taskMgr.remove("AIUpdate")
			self.props.setCursorHidden(False)
			self.win.requestProperties(self.props)
			self.mainMenu.showPauseGame()
			self.paused = True
		
	def restartGame(self):
		self.events.stop()
		self.taskMgr.remove("camera/control")
		self.taskMgr.remove("player/update")
		self.taskMgr.remove('hud')
		self.taskMgr.remove('player/flashlight/update')
		self.taskMgr.remove("AIUpdate")
		self.cleanResources()
		self.props.setCursorHidden(False)
		self.win.requestProperties(self.props)
		self.initGame()
	
	def cleanResources(self):
		self.AIworld = None
		del self.enemies [:]
		del self.rooms [:]
		self.enemies = None
		self.rooms = None
		self.player = None
		self.actions = None
		self.events = None
		self.mainMenu = None
		self.fog = None
		self.skydome.removeNode()
		self.amblight.removeNode()
		self.shadeless.removeNode()
		self.target1.removeNode()
		self.target2.removeNode()
		self.banana.removeNode()
		self.skydome = None
		self.amblight = None
		self.shadeless = None
		self.target1 = None
		self.target2 = None
		self.banana = None
		self.hud = None
		self.camctrl = None
		self.controls = None
		self.cTrav.clearColliders()
		gc.collect()
# >>>>>>> refs/remotes/origin/master

		self.taskMgr.add(self.player.updateAll, "player/update")
		self.taskMgr.add(self.player.flashlight.updatePower, 'player/flashlight/update')
		self.taskMgr.add(self.AIUpdate,"AIUpdate")
		self.taskMgr.add(self.camctrl.update, "camera/control")
		self.taskMgr.add(self.playerUpdate, "playerUpdate")

	def endGame(self):
		self.hud.hide()
		if (self.gameOver):
			self.image = OnscreenImage(image="assets/images/GameOver.png", pos = (0, 0, 0), parent=base.render2d, scale=(1,1,1))
		else:
			self.image = OnscreenImage(image="assets/images/to-be-continued.jpg", pos = (0, 0, 0), parent=base.render2d, scale=(1,1,1))
		self.startTimer(3)

		self.taskMgr.remove("camera/control")

	def menuDisplay(self, task):
		if (self.initTimer == False):
			hasFinished = self.timer()
			if (hasFinished):
				self.resetTimer()
				self.image.hide()
				self.props.setCursorHidden(False)
				self.props.setMouseMode(self.props.M_absolute)
				self.win.requestProperties(self.props)
				self.mainMenu.show()

		return task.cont

	def timer(self):
		currentTime = time.time()
		diff = currentTime - self.time
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

	def distance(self, p1, p2):
		#print "p1: ", p1
		#print "p2: ", p2    
		d = (p1.x - p2.x)**2  + (p1.y - p2.y)**2 + (p1.z - p2.z)**2
		return math.sqrt(d)

	def playerUpdate(self, task):
		reached = self.checkGoal()
		if (reached):
			self.player.die()
			self.endGame()
			return task.done
		someKey = False
		for key in self.actions.keys:
			if (key.wasPicked()):
				someKey = True
		self.hud.setKey(someKey)

		return task.cont

	def checkGoal(self):
# 		dist = self.distance(self.player.getNodePath().getPos(), self.goal.getPos())
# 		radius = 40
# 		if (dist < radius):
# 			self.gameOver = False
# 			return True
		return False

MetalSlender().run()