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

menu = interface.Interface()
lights = lighting.Lighting()

floorHandler = collisionSystem.floorHandler
wallHandler = collisionSystem.wallHandler

#** Collision masks
FLOOR_MASK=collisionSystem.FLOOR_MASK
WALL_MASK=collisionSystem.WALL_MASK

class MetalSlender(DirectObject):
		
	def __init__(self):
		# Preliminary capabilities check.
		if not self.initMessages(): 
			return

		self.initConfig()

		# Load the scene.
		self.room = scene_obj.SceneObj("room", "lcg12")	
		self.room.setTerrainCollision("**/ExtWalls","**/Floor", WALL_MASK,FLOOR_MASK)

		self.player  = Player(name = "player", model_path = "models/ralph", pos = Vec3(-30,45,126), scale = 3)
		self.camctrl = CameraControls(self.player)
		self.hud     = HUD(self.player)


		self.target1 = loader.loadModel("models/arrow")
		self.target1.setColor(1,0,0)
		self.target1.setPos(-76.1808, -52.1483, -14.4758)
		self.target1.setScale(5)
		self.target1.reparentTo(render)
		# Target2
		self.target2 = loader.loadModel("models/arrow")
		self.target2.setColor(0,1,0)
		self.target2.setPos(-40,50,-15)
		self.target2.setScale(5)
		self.target2.reparentTo(render)

		#self.target1.hide()
		#self.target2.hide()

		self.enemy = Enemy(Vec3(-76.1808, -52.1483, -14.4758), [self.target1, self.target2])


		self.AIworld = AIWorld(render)

		self.AIworld.addAiChar(self.enemy.getHooded())


		taskMgr.add(self.AIUpdate,"AIUpdate")

		# User controls

		self.addCommands()

		lights.setAmbientlight()
		lights.addSpotlight("Spot", base.cam)

		render.setShaderAuto()

	def initConfig(self):
		base.cTrav = CollisionTraverser()
	
		base.setBackgroundColor(0,0,0.2,1)
	
		base.camLens.setNearFar(0.001,1000)
		base.camLens.setFov(75)

		base.disableMouse()

		props = WindowProperties()
		props.setCursorHidden(True)

		base.win.requestProperties(props)
		
	def addCommands(self):
		self.accept('escape', sys.exit)
		self.accept('f', self.actionKeys, ['f'])

	def actionKeys(self, key):
		if key == 'f':
			self.player.fear = min(self.player.fear + 0.1, 1.0)
		
	#TODO: Verify if video features are supported
	def initMessages(self):
		self.inst_m = menu.addInstructions(0.95 , '[WASD]: walk')
		self.inst_h = menu.addInstructions(0.90 , 'SPACE: jump')
		self.inst_h = menu.addInstructions(0.85 , 'SHIFT+[WASD]: run' )
		self.inst_h = menu.addInstructions(0.80 , 'F: increase fear' )

		return True

	def AIUpdate(self,task):
		self.enemy.update()
		self.AIworld.update()            
		return task.cont


MetalSlender()
run()
