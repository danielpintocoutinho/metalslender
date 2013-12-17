#!/usr/bin/ppython
import panda3d
from panda3d.core import TransparencyAttrib
from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage

class HUD(DirectObject):
	#TODO: Preload all images
	#TODO: Find out how many sprites are available
	#TODO: Parameters to againrol screen resolution?
	def __init__(self, base, player):
		self.base   = base
		self.player = player

		self.heartmax = 160
		self.heartmin = 80
		self.heartbpm = self.heartmin
		self.heartaccum = 0
		self.last = 0
		self.heartbasis = 'assets/images/heartbeat2-%d.png'
		self.heartframe = 0
		self.heartimage = OnscreenImage(self.heartbasis % (1,), scale=(0.1,1,0.1), pos=(0,1,-0.8))
		self.text = OnscreenText('', pos=(0, -0.975), scale=0.05, fg=(0,1,0,1),	bg=(0,0,0,1))

		self.base.taskMgr.add(self.update, 'hud')

	def update(self, task):
		if self.player.isAlive():
			elapsed = task.time - self.last
			self.last = task.time

			# After a certain point, it should be cleared
			# Fear must also increase heartbeat
			f, b = self.player.fear, self.player.breath
			bpm = 80 + 200 * (0.75 + 0.25 * f) * (1 - b) + 40 * f

			self.heartaccum += elapsed * (bpm + self.heartbpm) / 2.0
			self.heartbpm = bpm
			self.heartframe = int(8 * self.heartaccum / 60) % 8
			self.heartimage.setImage(self.heartbasis % (self.heartframe + 1,))
			self.heartimage.setTransparency(TransparencyAttrib.MAlpha)

			#TODO: Update parameters
			heartampl = self.heartmax - self.heartmin
			if self.heartbpm < self.heartmax:
				s = float(self.heartbpm - self.heartmin) / heartampl
				self.text.setFg((s,1,0,1))
			else:
				s = float(self.heartbpm - self.heartmax) / heartampl
				self.text.setFg((1,1-s,0,1))

			self.text.setText('%d BPM' % (self.heartbpm,))
		else:
			self.text.setFg((1,1,1,1))
			self.text.setText('0 BPM')
			#TODO: send a 'death' event and, possibly, play back a nice heart stopping animation
			#return task.done

		self.heartimage.show()
		self.text.show()

		return task.cont
	
	def __del__(self):
		self.base   = None
		self.player = None
		self.heartimage.destroy()
		self.text.destroy()