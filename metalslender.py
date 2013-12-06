#!/usr/bin/ppython
from pandac.PandaModules import AmbientLight, Vec3, Vec4, CollisionTraverser, WindowProperties
# loadPrcFileData("", "prefer-parasite-buffer #f")

from direct.showbase.ShowBase import ShowBase

from hud import HUD
from player import Player
from camera import CameraControls
from eventsManager import EventManager

#TODO: Review these files
import scene_obj
import scene_actor
import animation_data
import interface
import collisionSystem

# menu = interface.Interface()

floorHandler = collisionSystem.floorHandler
wallHandler = collisionSystem.wallHandler

#** Collision masks
FLOOR_MASK=collisionSystem.FLOOR_MASK
WALL_MASK=collisionSystem.WALL_MASK

class MetalSlender(ShowBase):
		
	def __init__(self):
		ShowBase.__init__(self)
		
		# Preliminary capabilities check.
		if not self.initMessages(): 
			return
		
		self.initConfig()

		# Load the scene.
		self.room = scene_obj.SceneObj("room", "temp/stairs", self.render, scale=3.0)	
# 		self.room.setTerrainCollision("**/ExtWalls","**/Floor", WALL_MASK,FLOOR_MASK)
		self.room.setTerrainCollision("**/ExtWalls","**/Ramp.*", WALL_MASK,FLOOR_MASK)
		
		self.player  = Player("player", '', self.render)
		self.camctrl = CameraControls(self.player)
		self.hud     = HUD(self.player)
		
		EventManager(self.player).start()
		
		# User controls
		self.addCommands()
		
		self.setBackgroundColor(0,0,0)
		self.setAmbientlight((0.4, 0.4, 0.4, 1.0))

		self.render.setShaderAuto()

	def initConfig(self):
		self.cTrav = CollisionTraverser()
	
		self.setBackgroundColor(0,0,0.2,1)
	
		self.camLens.setNearFar(0.001,1000)
		self.camLens.setFov(75)

		self.disableMouse()
		self.win.movePointer(0, 100, 100)

		props = WindowProperties()
		props.setCursorHidden(True)

		self.win.requestProperties(props)
		
	def addCommands(self):
		self.accept('escape', self.userExit)
		self.accept('f', self.actionKeys, ['f'])

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
	
	def setAmbientlight(self, color = Vec4(0.01, 0.01, 0.01, 1)):
		alight = AmbientLight("Ambient")
		alight.setColor(color)
		alight = self.render.attachNewNode(alight)
		self.render.setLight(alight)

MetalSlender().run()
