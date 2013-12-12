#!/usr/bin/ppython
from direct.showbase.ShowBase import ShowBase
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
		self.enemies = []

		#TODO: Many things are only done once the game is started
		# Load the scene.
		self.rooms = []
		self.rooms.append(Room(self, "LCG"    , "temp/lcg13" , self.render))
		self.rooms.append(Room(self, "Bloco H", "temp/blocoh", self.render))
		
		#TODO: Support multiple rooms
		self.player  = Player(self, name = "player", pos = Vec3(90,90,12), model='', scene=self.render)
		self.actions = ActionManager(self, self.rooms[0].model, self.player)
		
		self.taskMgr.add(self.player.updateAll, "player/update")
		self.taskMgr.add(self.player.flashlight.updatePower, 'player/flashlight/update')
		
		EventManager(self, self.player, self.actions).start()

		#TODO: Only test code
		self.placeTargets()

# 		self.enemy = Enemy(Vec3(-76.1808, -52.1483, -14.4758), [self.target1, self.target2])
# 		self.AIworld.addAiChar(self.enemy.getHooded())

		self.mainMenu = MainMenu(self)
		#self.mainMenu.hide()

		self.taskMgr.add(self.player.updateAll, "player/update")
		self.taskMgr.add(self.player.flashlight.updatePower, 'player/flashlight/update')
		self.taskMgr.add(self.AIUpdate,"AIUpdate")

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
	def setupLighting(self, color = Vec4(0.35, 0.35, 0.35, 1)):
		alight = AmbientLight("AmbientLight")
		alight.setColor(color)
		alight = self.render.attachNewNode(alight)
		self.render.setLight(alight)
		
		#This light may be used by shadeless materials
		alight = AmbientLight("ShadelessLight")
		alight.setColor((1.0,1.0,1.0,1.0))
		self.shadeless = self.render.attachNewNode(alight)
		
	def placeTargets(self):
		self.target1 = self.loader.loadModel("assets/chicken/arrow")
		self.target1.setColor(1,0,0)
		self.target1.setPos(-76.1808, -52.1483, -14.4758)
		self.target1.setScale(5)
		self.target1.reparentTo(self.render)

		self.target1 = self.loader.loadModel("assets/chicken/arrow")
		self.target1.setColor(1,0,0)
		self.target1.setPos(23.3466,  30.4134, -14.4758)
		self.target1.setScale(5)
		self.target1.reparentTo(self.render)

		# Target2
		self.target2 = self.loader.loadModel("assets/chicken/arrow")
		self.target2.setColor(0,1,0)
		self.target2.setPos(23.3466, -85.0269, -14.4758)
		self.target2.setScale(5)
		self.target2.reparentTo(self.render)

		self.banana = self.loader.loadModel("assets/chicken/banana")
		self.banana.setScale(20)
		self.banana.setPos(23.3466, -85.0269, -14.4758)
		self.banana.reparentTo(self.render)


	def initConfig(self):
		self.cTrav = CollisionTraverser()
		
		self.render.setShaderAuto()
	
		#TODO: Must be moved to player's camera
		self.camLens.setNearFar(CAM_NEAR,CAM_FAR)
		self.camLens.setFov(75)

		self.disableMouse()
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
		for enemy in self.enemies:
			enemy.update()
		self.AIworld.update()       
		return task.cont

	def newGame(self):
		self.hud      = HUD(self, self.player)
		self.controls = PlayerControls(self.player, self.actions)
		self.camctrl  = CameraControls(self, self.player)

		self.props.setCursorHidden(True)
		self.win.requestProperties(self.props)
		self.mainMenu.hide()
		
		self.taskMgr.add(self.camctrl.update, "camera/control")

MetalSlender().run()