#!/usr/bin/python
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
	(RESTFUL  , RUNNING) : -1.0 /  45,
	(TIRED    , STOPPED) :  1.0 /  90,
	(TIRED    , WALKING) :  1.0 / 120,
	(TIRED    , RUNNING) : -1.0 /  30,
	(EXHAUSTED, STOPPED) :  1.0 / 120,
	(EXHAUSTED, WALKING) :  1.0 / 160,
	(EXHAUSTED, RUNNING) : -1.0 /  15,
}

class HUD(DirectObject):
	#TODO: Preload all images
	#TODO: Find out how many sprites are available
	#TODO: Parameters to control screen resolution and positioning?
	#TODO: Variable heartspeed
	def __init__(self):
		self.heartbasis = 'assets/images/heartbeat2-%d.png'
		self.heartmax = 180
		self.heartmin = 60
		self.heartaccum = 0
		self.heartframe = 0
		self.heartimage = OnscreenImage(self.heartbasis % (1,), scale=0.2)

		self.text = OnscreenText('', pos=(0, -0.5), scale=0.05)

		self.lasttime = 0

		self.breath = 1.0
		self.fear   = 0.0

		#self.breathrate = 1.0 / 30
		self.fearrate   = -1.0 / 60

		self.accept('w', self.walk)
		#self.accept('w-repeat', self.walk)
		self.accept('shift-w', self.run)
		self.accept('w-up', self.stop)

		self.updateState(RESTFUL, STOPPED)

		taskMgr.add(self, 'HUD')

	def updateState(self, breath, movement):
		self.state = (breath, movement)
		self.breathrate = breathrates[self.state]

	def stop(self):
		self.updateState(self.state[0], STOPPED)

	def walk(self):
		self.updateState(self.state[0], WALKING)

	def run(self):
		self.updateState(self.state[0], RUNNING)

	def __call__(self, task):
		timelapse = task.time - self.lasttime
		self.lasttime = task.time

		oldbreath   = self.breath
		deltabreath = self.breathrate * timelapse
		deltafear   = self.fearrate   * timelapse
		self.breath = min(1.0, max(-self.fearrate, self.breath + deltabreath))
		self.fear   = min(1.0, max(           0.0, self.fear   + deltafear  ))

		heartampl = self.heartmax - self.heartmin
		deltaaccum = timelapse * (self.heartmin + heartampl * (1 - (oldbreath + self.breath) / 2))
		bpm = (1 - self.breath) * heartampl + self.heartmin
		self.heartaccum += deltaaccum
		self.heartframe = int(8 * self.heartaccum / 60) % 8
		self.heartimage.setImage(self.heartbasis % (self.heartframe + 1,))
		self.heartimage.setTransparency(TransparencyAttrib.MAlpha)

		if self.breath > self.fear:
			self.updateState(RESTFUL  , self.state[1])
		elif self.breath > 0:
			self.updateState(TIRED    , self.state[1])
		else:
			self.updateState(EXHAUSTED, self.state[1])

		self.text.setText('%d BPM' % (bpm, ))
		return task.cont

class HUDTest(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)
		self.status = HUD();
		#taskMgr.add(self.status, 'HUD')

HUDTest().run()
"""
import unittest as ut
from status import *
import panda3d

class HUDTest(ut.TestCase):
	def setUp(self):
		self.s0 = HUD()

	def testInitialState(self):
		self.assertTrue(self.s0.isRestful())
		self.assertTrue(self.s0.isAlive())
		self.assertFalse(self.s0.isDead())
		self.assertFalse(self.s0.isTired())
		self.assertFalse(self.s0.isExhausted())
		self.assertEqual(self.s0.breath, 1)
		self.assertEqual(self.s0.fear, 0)

if __name__ == '__main__':
	ut.main()
"""
