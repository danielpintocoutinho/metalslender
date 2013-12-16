#!/usr/bin/ppython
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import *
from panda3d.ai import *
from panda3d.core import AmbientLight, Vec3, Vec4, CollisionTraverser, \
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
		
		# Preliminary capabilities check.
		#if not self.initMessages(): 
		#	return
		self.initConfig()
		self.setupEnvironment()
		
		self.AIworld = AIWorld(self.render)


		self.initTimer = True
		self.time = 0
		self.gameOver = True

		self.setFrameRateMeter(True)
		self.taskMgr.add(self.menuDisplay, "menuDisplay")

# 		self.AIworld.addAiChar(self.enemy.getHooded())

		self.mainMenu = MainMenu(self)
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
		
		#TODO: Is it possible to use per-room fog?
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
	def setupLighting(self, color = Vec4(0.3, 0.3, 0.3, 1)):
		alight = AmbientLight("AmbientLight")
		alight.setColor(color)
		alight = self.render.attachNewNode(alight)
		self.render.setLight(alight)
		
		#This light may be used by shadeless materials
		alight = AmbientLight("ShadelessLight")
		alight.setColor((1.0,1.0,1.0,1.0))
		self.shadeless = self.render.attachNewNode(alight)
		

	def initConfig(self):
		self.cTrav = CollisionTraverser()
		
		self.render.setShaderAuto()
	
		#TODO: Must be moved to player's camera
		#self.camLens.setNearFar(CAM_NEAR,CAM_FAR)
		self.camLens.setFov(75)

		#self.disableMouse()
		self.win.movePointer(0, 100, 100)

		self.props = WindowProperties()
		self.props.setFullscreen(1)
		self.props.setSize(1920, 1080)
		self.props.setCursorHidden(False)
		self.props.setMouseMode(self.props.M_absolute)
		
		self.openMainWindow()
		self.win.requestProperties(self.props)
		self.graphicsEngine.openWindows()
		self.win.requestProperties(self.props)
		
	def addCommands(self):
		self.accept('escape', self.userExit)
		self.accept('g', self.endGame)
		self.accept('i', self.actionKeys, ['i'])

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
		
		self.enemies = []
		self.doors = []
		self.keys = []

		#TODO: Many things are only done once the game is started
		# Load the scene.
		self.rooms = []
		self.rooms.append(Room(self, "LCG"    , "assets/chicken/lcg" , self.render))
		self.rooms.append(Room(self, "Bloco H", "assets/chicken/blocoh-pedro", self.render))
		
		for enemy in self.enemies:
			enemy.defineDynamicObjects("assets/chicken/lcg", "**/LCG_porta*")
		
		#TODO: Support multiple rooms
		self.player  = Player(self, name = "player", pos = Vec3(90,90,12), model='assets/chicken/coelho', scene=self.render)
		self.actions = ActionManager(self, self.rooms[0].model, self.player)
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
		self.mainMenu.hide()


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
			self.endGame()
			return task.done
		someKey = False
		for key in self.actions.keys:
			if (key.wasPicked()):
				someKey = True
		self.hud.setKey(someKey)

		return task.cont

	def checkGoal(self):
		dist = self.distance(self.player.getNodePath().getPos(), self.goal.getPos())
		radius = 40
		if (dist < radius):
			self.gameOver = False
			return True
		return False



MetalSlender().run()
