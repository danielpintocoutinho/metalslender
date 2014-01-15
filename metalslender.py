#!/usr/bin/ppython
import gc
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import *
from panda3d.ai import *
from panda3d.core import AmbientLight, CollisionNode, CollisionPlane, Plane, Vec3, Vec4, Mat4, CollisionTraverser, \
	WindowProperties, AntialiasAttrib, Fog, Texture, TextureStage

from MainMenu import MainMenu
from actionsManager import ActionManager
from collision import CollisionMask
from controls import CameraControls, PlayerControls
from constants import *
from door import Door
from enemy import Enemy
from eventsManager import EventManager
from hud import HUD
import interface
from player import Player
from room import Room
import time
import math

#TODO: Review game state transitions
CAM_NEAR=0.1
CAM_FAR =1000

CAM_NEAR = 0.1
CAM_FAR  = 1000

class MetalSlender(ShowBase):
	
	VERSION=0.1
	
	def __init__(self):
		ShowBase.__init__(self)
		self.initVideo()
		self.initGame()
	
	def initVideo(self):
		self.render.setShaderAuto()
		#TODO: Not working
		self.render.setAntialias(AntialiasAttrib.MMultisample)

		self.props = WindowProperties()

		self.props.setFullscreen(True)
 		self.props.setSize(1920, 1080)
		self.props.setCursorHidden(False)
		self.props.setMouseMode(self.props.M_absolute)
		
		self.win.requestProperties(self.props)
		self.win.movePointer(0, 100, 100)

	def initGame(self):
		self.paused = False
		self.initTimer = True
		self.time = 0
		self.gameOver = True

		self.setFrameRateMeter(True)
		self.taskMgr.add(self.menuDisplay, "menuDisplay")

		self.mainMenu = MainMenu(self)
		
		self.introSound = self.loader.loadSfx('assets/sounds/intro.mp3')
		self.introSound.setLoop(True)
		self.introSound.play()
		
	#TODO: Refactor environment into a class that inherits from nodepath
	def setupEnvironment(self):
		self.setBackgroundColor(0,0,0)
		self.setupLighting()
		self.setupFog()
		self.setupSkydome()
		self.setupPhysics()
		
	def setupFog(self):
		self.fog = Fog("fog")

		self.fog.setColor(FOG_COLOR)
		self.fog.setExpDensity(FOG_EXP_DENSITY)

		self.render.setFog(self.fog)
		
	def setupSkydome(self):
		self.skydome = self.loader.loadModel(EGG_SKYDOME)
		self.skydome.setBin('background', 0)
		self.skydome.setDepthWrite(False)
		self.skydome.reparentTo(self.cam)
		self.skydome.setCompass()
		self.skydome.setLight(self.shadeless)
		
	def setupLighting(self):
		alight = AmbientLight("AmbientLight")
		alight.setColor(AMBIENT_LIGHT)
		self.amblight = self.render.attachNewNode(alight)
		self.render.setLight(self.amblight)
		
		alight = AmbientLight("ShadelessLight")
		alight.setColor((1.0, 1.0, 1.0, 1.0))
		self.shadeless = self.render.attachNewNode(alight)
		
	def setupPhysics(self):
		self.cTrav = CollisionTraverser()
		
		plane = self.render.attachNewNode(CollisionNode('WorldBottom'))
		plane.node().addSolid(CollisionPlane(Plane(0, 0, 1, 30)))
		plane.node().setIntoCollideMask(CollisionMask.FLOOR)
		
	def loadScenario(self):
		self.rooms = []
		
		self.rooms.append(Room(self, self.render, "LCG"     , "assets/chicken/lcg-pedro"))
		self.rooms.append(Room(self, self.render, "Bloco H" , "assets/chicken/blocoh-pedro"))
		self.rooms.append(Room(self, self.render, "Bloco H2", "assets/chicken/blocoh2-pedro"))
		
	def addCommands(self):
		self.accept('escape', self.userExit)
		self.accept('g', self.endGame)
		self.accept('i', self.actionKeys, ['i'])
		self.accept('p', self.pauseGame)
		self.accept('z', self.restartGame)
		
		self.cTrav.setRespectPrevTransform(True)
		
	def addTasks(self):
		self.taskMgr.add(self.camctrl.update, "camera/control")
		self.taskMgr.add(self.player.updateAll, "player/update")
		self.taskMgr.add(self.hud.update, 'hud')
		self.taskMgr.add(self.player.flashlight.updatePower, 'player/flashlight/update')
		self.taskMgr.add(self.AIUpdate,"AIUpdate")
		self.taskMgr.add(self.camctrl.update, "camera/control")

	def actionKeys(self, key):
		if key == 'i':
			self.player.fear = min(self.player.fear + 0.1, 1.0)

	def AIUpdate(self,task):
		hasAttacked = []
		for enemy in self.enemies:
			attack = enemy.update()
			hasAttacked.append(attack)
		for i in hasAttacked:
			if (i == True):
				self.player.hurt()#TODO:The enemy itself should hurt the player
				#attack
		self.AIworld.update()
		if (not self.taskMgr.hasTaskNamed("player/update")):
			for enemy in self.enemies:
				enemy.stop()
			self.endGame()
			return task.done
		return task.cont

	def newGame(self):
		
		self.setupEnvironment()
		
		self.AIworld = AIWorld(self.render)
		
		self.introSound.stop()
		#TODO: Play creepy sound
# 		initialSound = loader.loadSfx('assets/sounds/enemies/nazgul_scream.mp3')
# 		initialSound.play()

		self.enemies = []
		self.items = []
		self.keys = []

		#TODO: Many things are only done once the game is started
		# Load the scene.
		self.loadScenario()

		for enemy in self.enemies:
			enemy.addDynamicObjects(self.render.findAllMatches('**/LCG_porta*'))
		
		self.player  = Player(self, self.render, 'Player')
		self.actions = ActionManager(self, self.player, self.rooms)
		
		self.em = EventManager(self, self.player, self.actions, self.rooms)
		self.em.start()

		for enemy in self.enemies:
			enemy.start()

		self.hud      = HUD(self, self.player)
		self.controls = PlayerControls(self.player, self.actions)
		self.camctrl  = CameraControls(self, self.player)

		self.props.setCursorHidden(True)
		self.win.requestProperties(self.props)

		self.mainMenu.hideNewGame()
		
		self.addTasks()
		self.addCommands()
		
# 		self.cTrav = None
	
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
				self.mainMenu.showNewGame()

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
		d = (p1.x - p2.x)**2  + (p1.y - p2.y)**2 + (p1.z - p2.z)**2
		return math.sqrt(d)

	def playerUpdate(self, task):
		reached = self.checkGoal()
		if (reached):
# 			self.player.die()
			self.endGame()
			return task.done
		someKey = False
		for key in self.actions.keys:
			if (key.wasPicked()):
				someKey = True
		self.hud.setKey(someKey)

		return task.cont

	def checkGoal(self):
		print 'To be continued...'
# 		dist = self.distance(self.player.getNodePath().getPos(), self.goal.getPos())
# 		radius = 40
# 		if (dist < radius):
# 			self.gameOver = False
# 			return True
		return False

MetalSlender().run()