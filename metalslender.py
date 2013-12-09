#!/usr/bin/ppython
from pandac.PandaModules import AmbientLight, Vec3, Vec4, CollisionTraverser, WindowProperties
# loadPrcFileData("", "prefer-parasite-buffer #f")

from direct.showbase.ShowBase import ShowBase

from hud import HUD
from player import Player
from camera import CameraControls
from door import Door
from eventsManager import EventManager
from controls import PlayerControls
from actionsManager import ActionManager

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
		self.room = scene_obj.SceneObj("room", "assets/chicken/lcg13", self.render)
		self.blocoh = scene_obj.SceneObj("blocoh", "assets/chicken/blocoh", self.render)
		self.room.setTerrainCollision("**/LCG_walls_int","**/LCG_floor_01", WALL_MASK,FLOOR_MASK)
		#self.blocoh.setTerrainCollision("**/H_corredor.003","**/H_floor_01", WALL_MASK,FLOOR_MASK)
		
		self.actions = ActionManager(self, self.room.getNodePath())
		self.player  = Player(actMng = self.actions, name = "player", pos = Vec3(90,90,12), model='', parent=self.render)
		self.controls = PlayerControls(self.player)
		self.camctrl = CameraControls(self.player)
		self.hud     = HUD(self.player)
		
		self.taskMgr.add(self.player.updateAll, "player/update")
		self.taskMgr.add(self.player.flashlight.updatePower, 'player/flashlight/update')
		
		EventManager(self, self.player, self.actions).start()
		
		# User controls
		self.addCommands()
		
		self.setBackgroundColor(0,0,0)
# 		self.setAmbientlight((0.4, 0.4, 0.4, 1.0))
		self.setAmbientlight()

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
	
	def setAmbientlight(self, color = Vec4(0.01, 0.01, 0.01, 1)):
		alight = AmbientLight("Ambient")
		alight.setColor(color)
		alight = self.render.attachNewNode(alight)
		self.render.setLight(alight)

MetalSlender().run()