from pandac.PandaModules import Vec3
from panda3d.core import BitMask32

from camera import CameraControls
from scene_obj import SceneObj
from hud import HUD

import collisionSystem

import panda3d
from panda3d.core import TransparencyAttrib
from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.task import Task

RESTFUL=0
TIRED=1
EXHAUSTED=2

STOPPED=0
WALKING=1
RUNNING=2

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

class Player(SceneObj):
	def __init__(self, name, model_path = '' , pos=Vec3(0,0,0), scale=1.0, source=render,actor=False):
		SceneObj.__init__(self, name, model_path, pos, scale, source, actor)

		self.heartmax = 160
		self.heartmin = 80
		self.heartbpm = self.heartmin
		self.heartaccum = 0

		self.breath = 1.0
		self.fear   = 0.0

		self.fearrate   = -1.0 / 60

		self.last = 0
		self.keys = [STOPPED] * 4
		
		self.updateState(RESTFUL)

		self.setObjCollision()
		self.setFloorCollision(collisionSystem.FLOOR_MASK, BitMask32.allOff())
		self.setWallCollision(collisionSystem.WALL_MASK, BitMask32.allOff())

		base.cam.reparentTo(self.getNodePath())
		base.cam.setPos(Vec3(0,0,5))
		#BUG: Shadows are cast with a positive offset on the z-axis
		#base.cam.setPos(pos + Vec3(0,0,25))

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

		#self.cons = CameraControls()
		#self.cons.start()

		self.focus = Vec3(55,-55,20)
		self.xrot = 180
		self.yrot = 0

		#TODO: Rename tasks
		taskMgr.add(self.taskAim, "player/aim")
		taskMgr.add(self.taskMove, "player/move")

	def isTired(self):
		return self.state == TIRED

	def isExhausted(self):
		return self.state == EXHAUSTED

	#TODO: Other methods like isDead()
	
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
		avatar = self.getNodePath()
		self.focus = avatar.getPos()
		#TODO: Bad code! Make the flashlight a child of the player
		flashlight = render.find("Spot")

		elapsed = task.time - self.last
		self.last = task.time

		if (self.keys[0]):
				dir = avatar.getMat().getRow3(1) #0 is x, 1 is y, 2 is z,
				dir.setZ(0)
				self.focus = self.focus + dir * elapsed*40 * self.keys[0]
				avatar.setFluidPos(self.focus )
		if (self.keys[1]):
				dir = avatar.getMat().getRow3(1)
				dir.setZ(0)
				self.focus = self.focus - dir * elapsed*40 * self.keys[1]
				avatar.setFluidPos(self.focus)
		if (self.keys[2]):
				dir = avatar.getMat().getRow3(0)
				dir.setZ(0)
				self.focus = self.focus - dir * elapsed*20 * self.keys[2]
				avatar.setFluidPos(self.focus)
		if (self.keys[3]):
				dir = avatar.getMat().getRow3(0)
				dir.setZ(0)
				self.focus = self.focus + dir * elapsed*20 * self.keys[3]
				avatar.setFluidPos(self.focus)
		
		# positions the flashlight with the player 
		flashlight.setFluidPos(avatar.getPos())
		flashlight.setZ(flashlight.getZ() + 4)
		flashlight.setHpr( avatar.getHpr())

		oldbreath   = self.breath
		deltabreath = self.breathrate * elapsed
		deltafear   = self.fearrate   * elapsed
		self.fear   = min(1.0, max(       0.0, self.fear   + deltafear  ))
		self.breath = min(1.0, max(-self.fear, self.breath + deltabreath))

		if self.breath == -1:
			self.heartbpm = 0
			#TODO: send a 'death' event and, possibly, play back a nice heart stopping animation
			return task.done
		else:
			heartampl = self.heartmax - self.heartmin
			deltaaccum = elapsed * (self.heartmin + heartampl * (1 - (oldbreath + self.breath) / 2))

			# After a certain point, it should be cleared
			# Fear must also increase heartbeat
			self.heartaccum += deltaaccum
			self.heartbpm = (1 - self.breath) * heartampl + self.heartmin

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

	def taskAim(self, task):
		md = base.win.getPointer(0)
		x = md.getX()
		y = md.getY()

		if base.win.movePointer(0, 100, 100):
			#TODO: Refactor these constants to a mouse sensitivity configuration screen
			self.xrot -= (x - 100) * 0.2
			self.yrot -= (y - 100) * 0.2
			self.yrot  = min(90, max(-90, self.yrot))

		self.getNodePath().setHpr(self.xrot, self.yrot, 0)
		
		return task.cont
	
	def jump(self):
		if self.getFloorHandler().isOnGround(): 
			self.getFloorHandler().addVelocity(25)
