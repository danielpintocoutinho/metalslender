#!/usr/bin/ppython
from panda3d.core import *
import sys
loadPrcFileData("", "prefer-parasite-buffer #f")

from direct.showbase.DirectObject import DirectObject

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

menu = interface.Interface()

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
		
		self.player  = Player(name = "player", pos = Vec3(-30,45,126))
		self.camctrl = CameraControls(self.player)
		self.hud     = HUD(self.player)
		
		EventManager(self.player).start()
		
		# User controls
		self.addCommands()
		
		base.setBackgroundColor(0,0,0)
		self.setAmbientlight()

		render.setShaderAuto()

	def initConfig(self):
		base.cTrav = CollisionTraverser()
	
		base.setBackgroundColor(0,0,0.2,1)
	
		base.camLens.setNearFar(0.001,1000)
		base.camLens.setFov(75)

		base.disableMouse()
		base.win.movePointer(0, 100, 100)

		props = WindowProperties()
		props.setCursorHidden(True)

		base.win.requestProperties(props)
		
	def addCommands(self):
		self.accept('escape', sys.exit)
		self.accept('f', self.actionKeys, ['f'])

	def actionKeys(self, key):
		if key == 'i':
			self.player.fear = min(self.player.fear + 0.1, 1.0)
		
	#TODO: Verify if video features are supported
	def initMessages(self):
		self.inst_m = menu.addInstructions(0.95 , '[WASD]: walk')
		self.inst_h = menu.addInstructions(0.90 , 'SPACE: jump')
		self.inst_h = menu.addInstructions(0.85 , 'SHIFT+[WASD]: run' )
		self.inst_h = menu.addInstructions(0.80 , 'F: Flashlight On/Off')
		self.inst_h = menu.addInstructions(0.75 , 'I: increase fear' )

		return True
	
	def setAmbientlight(self, color = Vec4(0.01, 0.01, 0.01, 1)):
		alight = AmbientLight("Ambient")
		alight.setColor(color)
		alight = render.attachNewNode(alight)
		render.setLight(alight)

MetalSlender()
run()
