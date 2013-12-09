#!/usr/bin/ppython
from panda3d.core import *
import sys
loadPrcFileData("", "prefer-parasite-buffer #f")

from direct.showbase.DirectObject import DirectObject

from hud import HUD
from player import Player
from camera import CameraControls
from enemy import Enemy

#TODO: Review these files
import scene_obj
import scene_actor
import animation_data
import interface
import lighting
import collisionSystem
from panda3d.ai import *
from MainMenu import MainMenu

menu = interface.Interface()
lights = lighting.Lighting()

floorHandler = collisionSystem.floorHandler
wallHandler = collisionSystem.wallHandler


wp = WindowProperties()
wp.setFullscreen(1)
wp.setSize(1920, 1080)
base.openMainWindow()
base.win.requestProperties(wp)
base.graphicsEngine.openWindows()


#** Collision masks
FLOOR_MASK=collisionSystem.FLOOR_MASK
WALL_MASK=collisionSystem.WALL_MASK


class MetalSlender(DirectObject):
		
	def __init__(self):
		# Preliminary capabilities check.
		#if not self.initMessages(): 
		#	return

		self.initConfig()

		# Load the scene.
		self.room = scene_obj.SceneObj("room", "lcg13")	
		self.room.setTerrainCollision("**/LCG_walls_ext","**/LCG_floor", WALL_MASK,FLOOR_MASK)

		self.player  = Player(name = "player", model_path = "assets/chicken/coelho", pos = Vec3(268.953, -6.29758, -14.0991), scale = 3)
		self.camctrl = CameraControls(self.player)
		self.hud     = HUD(self.player)


		self.target1 = loader.loadModel("assets/chicken/arrow")
		self.target1.setColor(1,0,0)
		self.target1.setPos(-76.1808, -52.1483, -14.4758)
		self.target1.setScale(5)
		self.target1.reparentTo(render)


		self.target1 = loader.loadModel("assets/chicken/arrow")
		self.target1.setColor(1,0,0)
		self.target1.setPos(23.3466,  30.4134, -14.4758)
		self.target1.setScale(5)
		self.target1.reparentTo(render)

		# Target2
		self.target2 = loader.loadModel("assets/chicken/arrow")
		self.target2.setColor(0,1,0)
		self.target2.setPos(23.3466, -85.0269, -14.4758)
		self.target2.setScale(5)
		self.target2.reparentTo(render)

		self.banana = loader.loadModel("assets/chicken/banana")
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


		taskMgr.add(self.AIUpdate,"AIUpdate")

		# User controls

		self.addCommands()

		lights.setAmbientlight()
		lights.addSpotlight("Spot", base.cam)

		render.setShaderAuto()


	def initConfig(self):
		base.cTrav = CollisionTraverser()
	
		base.setBackgroundColor(0,0,0.2,1)
	
		#base.camLens.setNearFar(0.001,1000)
		base.camLens.setFov(75)

		base.disableMouse()

		self.props = WindowProperties()
		self.props.setCursorHidden(False)
		wp.setMouseMode(self.props.M_absolute)

		base.win.requestProperties(self.props)

		
	def addCommands(self):
		self.accept('escape', sys.exit)
		self.accept('f', self.actionKeys, ['f'])

	def actionKeys(self, key):
		if key == 'f':
			self.player.fear = min(self.player.fear + 0.1, 1.0)
		
	#TODO: Verify if video features are supported
	#def initMessages(self):
	#	self.inst_m = menu.addInstructions(0.95 , '[WASD]: walk')
	#	self.inst_h = menu.addInstructions(0.90 , 'SPACE: jump')
	#	self.inst_h = menu.addInstructions(0.85 , 'SHIFT+[WASD]: run' )
	#	self.inst_h = menu.addInstructions(0.80 , 'F: increase fear' )

		return True

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
		base.win.requestProperties(self.props)
		self.mainMenu.hide()


MetalSlender()
run()
