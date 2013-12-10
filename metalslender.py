#!/usr/bin/ppython
from direct.showbase.ShowBase import ShowBase
from pandac.PandaModules import AmbientLight, Vec3, Vec4, CollisionTraverser, \
	WindowProperties

from MainMenu import MainMenu
from actionsManager import ActionManager
from camera import CameraControls
from controls import PlayerControls
from door import Door
from enemy import Enemy
from eventsManager import EventManager
from hud import HUD
import interface
from panda3d.ai import *
from player import Player
from room import Room

# loadPrcFileData("", "prefer-parasite-buffer #f")
#TODO: Review these files
CAM_NEAR=0.1
CAM_FAR =1000

class MetalSlender(ShowBase):
	
	VERSION=0.1
		
	def __init__(self):
		ShowBase.__init__(self)
		
		# Preliminary capabilities check.
		#if not self.initMessages(): 
		#	return

		self.initConfig()

		# Load the scene.
		self.rooms = []
		self.rooms.append(Room(self, "LCG"    , "assets/chicken/lcg13" , self.render))
		self.rooms.append(Room(self, "Bloco H", "assets/chicken/blocoh", self.render))
		
		#TODO: Support multiple rooms
		self.actions = ActionManager(self, self.rooms[0].model)
		self.player  = Player(self, actMng = self.actions, name = "player", pos = Vec3(90,90,12), model='', parent=self.render)
		self.controls = PlayerControls(self.player)
		self.camctrl = CameraControls(self.player)
		self.hud     = HUD(self.player)
		
		self.taskMgr.add(self.player.updateAll, "player/update")
		self.taskMgr.add(self.player.flashlight.updatePower, 'player/flashlight/update')
		
		EventManager(self, self.player, self.actions).start()

		self.target1 = self.loader.loadModel("assets/chicken/arrow")
		self.target1.setColor(1,0,0)
		self.target1.setPos(-76.1808, -52.1483, -14.4758)
		self.target1.setScale(5)
		self.target1.reparentTo(render)

		self.target1 = self.loader.loadModel("assets/chicken/arrow")
		self.target1.setColor(1,0,0)
		self.target1.setPos(23.3466,  30.4134, -14.4758)
		self.target1.setScale(5)
		self.target1.reparentTo(render)

		# Target2
		self.target2 = self.loader.loadModel("assets/chicken/arrow")
		self.target2.setColor(0,1,0)
		self.target2.setPos(23.3466, -85.0269, -14.4758)
		self.target2.setScale(5)
		self.target2.reparentTo(render)

		self.banana = self.loader.loadModel("assets/chicken/banana")
		self.banana.setScale(20)
		self.banana.setPos(23.3466, -85.0269, -14.4758)
		self.banana.reparentTo(render)

		#self.target1.hide()
		#self.target2.hide()

		self.enemy = Enemy(Vec3(-76.1808, -52.1483, -14.4758), [self.target1, self.target2])

		self.AIworld = AIWorld(render)

		self.AIworld.addAiChar(self.enemy.getHooded())

		self.mainMenu = MainMenu(self)
		#self.mainMenu.hide()

		self.taskMgr.add(self.AIUpdate,"AIUpdate")

		# User controls
		self.addCommands()
		
		self.setBackgroundColor(0,0,0)
# 		self.setAmbientlight((0.4, 0.4, 0.4, 1.0))
		self.setAmbientlight()

		self.render.setShaderAuto()

	def initConfig(self):
		self.cTrav = CollisionTraverser()
	
		self.setBackgroundColor(0,0,0.2,1)
	
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
	
	def setAmbientlight(self, color = Vec4(0.31, 0.31, 0.31, 1)):
		alight = AmbientLight("Ambient")
		alight.setColor(color)
		alight = self.render.attachNewNode(alight)
		self.render.setLight(alight)

	def AIUpdate(self,task):
		self.enemy.update()
		self.AIworld.update()            
		return task.cont

	def exit(self):
		self.mainMenu.__del__()
		exit()

	def newGame(self):
		self.camctrl.setMouseMovement(True)
		self.hud.showHud(True)
		self.props.setCursorHidden(True)
		self.win.requestProperties(self.props)
		self.mainMenu.hide()

MetalSlender().run()