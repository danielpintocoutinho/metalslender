from pandac.PandaModules import Vec3
from panda3d.core import BitMask32

from camera import CameraControls
from scene_obj import SceneObj
from hud import HUD
import collisionSystem

from direct.showbase.DirectObject import DirectObject

RESTFUL=0
TIRED=1
EXHAUSTED=2

STOPPED=0
WALKING=1
RUNNING=4

breathrates = {
	(RESTFUL  , STOPPED) :  1.0 /  60,
	(RESTFUL  , WALKING) :  1.0 /  80,
	(RESTFUL  , RUNNING) : -1.0 /  20,
	(TIRED    , STOPPED) :  1.0 /  90,
	(TIRED    , WALKING) :  1.0 / 120,
	(TIRED    , RUNNING) : -1.0 /  10,
	(EXHAUSTED, STOPPED) :  1.0 / 120,
	(EXHAUSTED, WALKING) :  1.0 / 160,
	(EXHAUSTED, RUNNING) : -1.0 /   5,
}

#TODO: Refactor things to improve SceneObj
class Player(SceneObj):
	def __init__(self, name, model_path = '' , pos=Vec3(0,0,0), scale=1.0, source=render,actor=False):
		SceneObj.__init__(self, name, model_path, pos, scale, source, actor)

		self.breath = 1.0
		self.fear   = 0.0

		self.fearrate   = -1.0 / 360

		self.last = 0
		self.keys = [STOPPED] * 4
		
		self.updateState(RESTFUL)

		self.setObjCollision()
		self.setFloorCollision(collisionSystem.FLOOR_MASK, BitMask32.allOff())
		self.setWallCollision(collisionSystem.WALL_MASK, BitMask32.allOff())

		base.cam.reparentTo(self.getNodePath())
		#BUG: Shadows are cast with a positive offset on the z-axis
		base.cam.setPos(Vec3(0,0,25))

		self.accept("w-up", self.setKeys, [0, STOPPED])
		self.accept("s-up", self.setKeys, [1, STOPPED])
		self.accept("a-up", self.setKeys, [2, STOPPED])
		self.accept("d-up", self.setKeys, [3, STOPPED])
		self.accept("shift-w-up", self.setKeys, [0, STOPPED])
		self.accept("shift-s-up", self.setKeys, [1, STOPPED])
		self.accept("shift-a-up", self.setKeys, [2, STOPPED])
		self.accept("shift-d-up", self.setKeys, [3, STOPPED])
		self.accept("w", self.setKeys, [0, WALKING])
		self.accept("s", self.setKeys, [1, WALKING])
		self.accept("a", self.setKeys, [2, WALKING])
		self.accept("d", self.setKeys, [3, WALKING])
		self.accept("shift-w", self.setKeys, [0, RUNNING])
		self.accept("shift-s", self.setKeys, [1, RUNNING])
		self.accept("shift-a", self.setKeys, [2, RUNNING])
		self.accept("shift-d", self.setKeys, [3, RUNNING])
		#TODO: Must taks your breath, also
		self.accept("space", self.jump)

		taskMgr.add(self.taskMove, "player/move")

	def isTired(self):
		return self.state == TIRED

	def isExhausted(self):
		return self.state == EXHAUSTED

	def isAlive(self):
		return self.breath > -1

	#TODO: Other methods like isDead()
	
	#TODO: If movement validation is enabled, the player must stop once it is
	# exhausted, which means it cannot run and die of fear. But if it isn't, the
	# player can continue running after it is tired.
	def validateMovement(self):
		if self.isExhausted():
			self.keys = [min(k, WALKING) for k in self.keys]

	def updateState(self, breath):
		self.state = breath
		self.validateMovement()
		self.breathrate = breathrates[(self.state, max(self.keys))]
				 
	def setKeys(self, btn, value):
		self.keys[btn] = value
		self.validateMovement()
				
	def taskMove(self, task):
		player = self.getNodePath()
		self.focus = player.getPos()
		#print player.getPos()
		#TODO: Bad code! Make the flashlight a child of the player
		#flashlight = render.find("Spot")

		elapsed = task.time - self.last
		self.last = task.time

		if (self.keys[0]):
				dir = player.getMat().getRow3(1) #0 is x, 1 is y, 2 is z,
				dir.setZ(0)
				self.focus = self.focus + dir * elapsed*40 * self.keys[0]
				player.setFluidPos(self.focus)
		if (self.keys[1]):
				dir = player.getMat().getRow3(1)
				dir.setZ(0)
				self.focus = self.focus - dir * elapsed*40 * self.keys[1]
				player.setFluidPos(self.focus)
		if (self.keys[2]):
				dir = player.getMat().getRow3(0)
				dir.setZ(0)
				self.focus = self.focus - dir * elapsed*20 * self.keys[2]
				player.setFluidPos(self.focus)
		if (self.keys[3]):
				dir = player.getMat().getRow3(0)
				dir.setZ(0)
				self.focus = self.focus + dir * elapsed*20 * self.keys[3]
				player.setFluidPos(self.focus)
		
		# positions the flashlight with the player 
		#flashlight.setFluidPos(player.getPos())
		#flashlight.setZ(flashlight.getZ() + 4)
		#flashlight.setHpr( player.getHpr())

		oldbreath   = self.breath
		deltabreath = self.breathrate * elapsed
		deltafear   = self.fearrate   * elapsed
		self.fear   = min(1.0, max(       0.0, self.fear   + deltafear  ))
		self.breath = min(1.0, max(-self.fear, self.breath + deltabreath))

		if self.isAlive():

			if self.breath > self.fear:
				self.updateState(RESTFUL)
			elif self.breath > 0:
				self.updateState(TIRED)
			elif self.breath >= -self.fear:
				self.updateState(EXHAUSTED)
			#TODO: Send an event saying that it can't run anymore
			else:
				pass

			return task.cont
		else:
			#TODO: send a 'death' event and, possibly, play back a nice heart stopping animation
			return task.done
	
	def jump(self):
		if self.getFloorHandler().isOnGround(): 
			self.getFloorHandler().addVelocity(25)
